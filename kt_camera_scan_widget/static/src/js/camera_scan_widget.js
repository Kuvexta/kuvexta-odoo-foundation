/** @odoo-module **/

import { useService } from "@web/core/utils/hooks";
import { Dialog } from "@web/core/dialog/dialog";
import { _t } from "@web/core/l10n/translation";
import {
    Component, useState, useRef, onMounted, onWillUnmount,
} from "@odoo/owl";
import { createBarcodeEngine } from "./camera_scan_service";

/**
 * Componente reutilizable de escaneo por cámara. NO tiene lógica de
 * negocio — solo captura video, decodifica, y emite el código
 * detectado hacia quien lo invocó (ver
 * DISENO_ARQUITECTURA_KT_CAMERA_SCAN_WIDGET.md, sección 2).
 *
 * Uso desde otro módulo (ej. kt_scanflow_documents):
 *
 *   import { openCameraScanDialog } from
 *       "@kt_camera_scan_widget/js/camera_scan_widget";
 *   const code = await openCameraScanDialog(this.env);
 *   if (code) { ... }
 *
 * NOTA DE DESPLIEGUE: probar en un dispositivo Android real (Chrome)
 * y, si es posible, uno iOS (Safari) antes de dar este componente por
 * terminado — ver plan de pruebas del diseño, sección 10.
 *
 * IMPORTANTE — bug real encontrado en producción (05/08/2026,
 * `gc.subienes.com`): el input de entrada manual (ver
 * `camera_scan_widget.xml`) usa `t-on-keydown.stop`, NO
 * `t-on-keydown` a secas — mismo motivo documentado en
 * `kt_scanflow_documents/static/src/js/scan_input_widget.js`: el
 * servicio nativo de Odoo que escucha lectores físicos de código de
 * barras (`addons/barcodes/static/src/barcode_service.js`) comparte
 * un buffer global entre CUALQUIER input de la página, y escribir en
 * un input normal mientras ese buffer tiene algo pendiente puede
 * hacer que ese servicio llame `target.getAttribute(...)` sobre un
 * `target` que quedó en `null`, lanzando un `TypeError` sin relación
 * aparente con este widget.
 */
const SCAN_COOLDOWN_MS = 1500;
const DETECT_INTERVAL_MS = 200;

export class KtCameraScanWidget extends Component {
    static template = "kt_camera_scan_widget.CameraScanWidget";
    static props = {
        facingMode: { type: String, optional: true },
        beepEnabled: { type: Boolean, optional: true },
        onDetected: Function,
        onClose: { type: Function, optional: true },
    };
    static defaultProps = {
        facingMode: "environment",
        beepEnabled: true,
    };

    setup() {
        this.notification = useService("notification");
        this.videoRef = useRef("kt_camera_video");
        this.state = useState({
            manualCode: "",
            hasEngine: false,
            hasTorch: false,
            torchOn: false,
            status: "starting",
            errorMessage: "",
        });
        this._engine = null;
        this._stream = null;
        this._detectTimer = null;
        this._lastCode = null;
        this._lastCodeAt = 0;

        onMounted(() => {
            // La cámara y el motor de decodificación se resuelven en
            // paralelo — el motor (sobre todo la capa 2, ZBar/WASM)
            // puede tardar en cargar, y no hace sentido bloquear el
            // encendido de la cámara mientras tanto.
            this._loadEngine();
            this._startCamera();
        });
        onWillUnmount(() => this._stopCamera());
    }

    async _loadEngine() {
        this._engine = await createBarcodeEngine();
        this.state.hasEngine = !!this._engine;
        this._maybeStartDetectLoop();
    }

    async _startCamera() {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            this.state.status = "unsupported";
            return;
        }
        try {
            this._stream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: this.props.facingMode },
                audio: false,
            });
        } catch (error) {
            this.state.status = "error";
            this.state.errorMessage = error?.message || String(error);
            return;
        }
        const videoEl = this.videoRef.el;
        if (!videoEl) {
            return;
        }
        videoEl.srcObject = this._stream;
        await videoEl.play();
        this.state.status = "running";

        const [track] = this._stream.getVideoTracks();
        if (track && typeof track.getCapabilities === "function") {
            const capabilities = track.getCapabilities();
            this.state.hasTorch = !!capabilities.torch;
        }

        this._maybeStartDetectLoop();
    }

    _maybeStartDetectLoop() {
        if (this._detectTimer || !this._engine || this.state.status !== "running") {
            return;
        }
        this._detectTimer = setInterval(() => this._detectFrame(), DETECT_INTERVAL_MS);
    }

    _stopCamera() {
        if (this._detectTimer) {
            clearInterval(this._detectTimer);
            this._detectTimer = null;
        }
        if (this._stream) {
            this._stream.getTracks().forEach((track) => track.stop());
            this._stream = null;
        }
    }

    async _detectFrame() {
        const videoEl = this.videoRef.el;
        if (!videoEl || videoEl.readyState < 2) {
            return;
        }
        let codes;
        try {
            codes = await this._engine.detect(videoEl);
        } catch {
            return;
        }
        if (codes && codes.length) {
            this._onCodeDetected(codes[0]);
        }
    }

    _onCodeDetected(code) {
        const now = Date.now();
        if (code === this._lastCode && now - this._lastCodeAt < SCAN_COOLDOWN_MS) {
            // Mismo código todavía en cuadro dentro del período de
            // "cooldown" — se ignora para no agregarlo varias veces.
            return;
        }
        this._lastCode = code;
        this._lastCodeAt = now;
        this._feedbackSuccess();
        this.props.onDetected(code);
    }

    _feedbackSuccess() {
        if (this.props.beepEnabled) {
            this._beep();
        }
        if (navigator.vibrate) {
            navigator.vibrate(80);
        }
    }

    _beep() {
        try {
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = ctx.createOscillator();
            oscillator.frequency.value = 1200;
            oscillator.connect(ctx.destination);
            oscillator.start();
            setTimeout(() => {
                oscillator.stop();
                ctx.close();
            }, 100);
        } catch {
            // Algunos navegadores bloquean AudioContext sin
            // interacción previa del usuario — el escaneo sigue
            // funcionando igual, solo sin sonido.
        }
    }

    async toggleTorch() {
        if (!this._stream) {
            return;
        }
        const [track] = this._stream.getVideoTracks();
        if (!track) {
            return;
        }
        const newState = !this.state.torchOn;
        try {
            await track.applyConstraints({ advanced: [{ torch: newState }] });
            this.state.torchOn = newState;
        } catch {
            this.notification.add(
                _t("Esta cámara no soporta control de linterna."),
                { type: "warning" }
            );
        }
    }

    submitManualCode() {
        const code = (this.state.manualCode || "").trim();
        if (!code) {
            return;
        }
        this.state.manualCode = "";
        this.props.onDetected(code);
    }

    close() {
        this._stopCamera();
        if (this.props.onClose) {
            this.props.onClose();
        }
    }
}

/**
 * Modal que envuelve `KtCameraScanWidget` en un `Dialog` estándar de
 * Odoo — es lo que normalmente se quiere usar desde otro módulo (ver
 * `openCameraScanDialog` más abajo), en vez de instanciar el
 * componente de escaneo directamente.
 */
class KtCameraScanDialog extends Component {
    static template = "kt_camera_scan_widget.CameraScanDialog";
    static components = { Dialog, KtCameraScanWidget };
    static props = {
        close: Function,
        facingMode: { type: String, optional: true },
        beepEnabled: { type: Boolean, optional: true },
        onDetected: Function,
    };

    onDetected(code) {
        this.props.onDetected(code);
    }
}

/**
 * Abre el diálogo de escaneo por cámara y devuelve una Promise que se
 * resuelve con el primer código detectado (o entrada manual), o con
 * `null` si el usuario cierra el diálogo sin escanear nada.
 *
 * @param {import("@web/env").OdooEnv} env
 * @param {{facingMode?: string, beepEnabled?: boolean}} [options]
 */
export function openCameraScanDialog(env, options = {}) {
    return new Promise((resolve) => {
        let resolved = false;
        const removeDialog = env.services.dialog.add(KtCameraScanDialog, {
            facingMode: options.facingMode || "environment",
            beepEnabled: options.beepEnabled !== false,
            onDetected: (code) => {
                resolved = true;
                resolve(code);
                removeDialog();
            },
        }, {
            onClose: () => {
                if (!resolved) {
                    resolve(null);
                }
            },
        });
    });
}
