/** @odoo-module **/

import { rpc } from "@web/core/network/rpc";
import publicWidget from "@web/legacy/js/public/public_widget";
import { createBarcodeEngine } from "@kt_camera_scan_widget/js/camera_scan_service";

const DETECTION_INTERVAL_MS = 220;
const REPEAT_WINDOW_MS = 1600;

publicWidget.registry.KtCameraWebsiteBase = publicWidget.Widget.extend({
    selector: ".kt_camera_website_base",
    events: {
        "click .kt_camera_website_open": "_openDialog",
        "click .kt_camera_website_submit": "_submitManualCode",
        "click .kt_camera_website_torch": "_toggleTorch",
        "keydown .kt_camera_website_manual": "_manualKeydown",
    },

    init() {
        this._super(...arguments);
        this._busy = false;
        this._detector = null;
        this._dialog = null;
        this._lastCode = "";
        this._lastDetectionAt = 0;
        this._scanTimer = null;
        this._stream = null;
        this._torchEnabled = false;
    },

    destroy() {
        this._stopCamera();
        this._super(...arguments);
    },

    _openDialog(ev) {
        ev.preventDefault();
        const dialogElement = this.el.querySelector(".kt_camera_website_dialog");
        if (!dialogElement || !window.bootstrap) {
            return;
        }
        this._dialog = window.bootstrap.Modal.getOrCreateInstance(dialogElement);
        dialogElement.addEventListener("shown.bs.modal", () => this._startCamera(), {
            once: true,
        });
        dialogElement.addEventListener("hidden.bs.modal", () => this._stopCamera(), {
            once: true,
        });
        this._setStatus("Preparando la cámara…");
        this._dialog.show();
    },

    _manualKeydown(ev) {
        // Prevent a backend/global barcode listener from consuming this input.
        ev.stopPropagation();
        if (ev.key === "Enter") {
            ev.preventDefault();
            this._submitManualCode();
        }
    },

    async _submitManualCode() {
        const input = this.el.querySelector(".kt_camera_website_manual");
        const code = (input?.value || "").trim();
        if (!code) {
            this._setStatus("Escriba un código antes de buscar.");
            input?.focus();
            return;
        }
        if (input) {
            input.value = "";
        }
        await this._resolve(code);
    },

    async _startCamera() {
        this._stopCamera();
        const video = this.el.querySelector(".kt_camera_website_video");
        if (!video) {
            return;
        }
        this._setStatus("Cargando el lector…");
        try {
            this._detector = await createBarcodeEngine();
        } catch {
            this._detector = null;
        }
        if (!this._detector || !navigator.mediaDevices?.getUserMedia) {
            this._setStatus("La cámara no está disponible. Puede escribir el código abajo.");
            this.el.querySelector(".kt_camera_website_manual")?.focus();
            return;
        }

        try {
            this._stream = await navigator.mediaDevices.getUserMedia({
                audio: false,
                video: { facingMode: this.el.dataset.facing || "environment" },
            });
        } catch {
            this._setStatus("No fue posible abrir la cámara. Revise el permiso o escriba el código.");
            this.el.querySelector(".kt_camera_website_manual")?.focus();
            return;
        }

        video.srcObject = this._stream;
        await video.play().catch(() => {});
        this._setStatus("Apunte la cámara al código.", true);
        this._configureTorch();
        this._scanTimer = window.setInterval(
            () => this._detect(video),
            DETECTION_INTERVAL_MS
        );
    },

    async _detect(video) {
        if (!this._detector || this._busy) {
            return;
        }
        let detected = [];
        try {
            detected = await this._detector.detect(video);
        } catch {
            return;
        }
        const code = detected[0];
        if (!code) {
            return;
        }
        const now = Date.now();
        if (code === this._lastCode && now - this._lastDetectionAt < REPEAT_WINDOW_MS) {
            return;
        }
        this._lastCode = code;
        this._lastDetectionAt = now;
        await this._resolve(code);
    },

    async _resolve(code) {
        if (this._busy) {
            return;
        }
        this._busy = true;
        this._setStatus("Buscando un producto publicado…");
        let result;
        try {
            result = await rpc("/kt/camera/v1/product/resolve", { code });
        } catch {
            result = null;
        } finally {
            this._busy = false;
        }

        if (result?.status === "found" && result.product_url) {
            this._beep();
            this._stopCamera();
            this._dialog?.hide();
            window.location.assign(result.product_url);
            return;
        }

        const messages = {
            ambiguous: "Ese código corresponde a varios productos. Corrija los códigos duplicados.",
            disabled: "El escaneo por cámara está deshabilitado para esta empresa.",
            invalid: "El código está vacío, es demasiado largo o contiene caracteres no válidos.",
            not_found: "No se encontró un producto publicado con ese código.",
        };
        this._setStatus(
            messages[result?.status] ||
                "No se pudo consultar el catálogo. Intente de nuevo."
        );
        if (result?.status === "disabled") {
            this._stopCamera();
        }
        this.el.querySelector(".kt_camera_website_manual")?.focus();
    },

    _setStatus(message, running = false) {
        const status = this.el.querySelector(".kt_camera_website_status");
        if (!status) {
            return;
        }
        status.textContent = message;
        status.classList.toggle("is-running", running);
    },

    _configureTorch() {
        const button = this.el.querySelector(".kt_camera_website_torch");
        const track = this._stream?.getVideoTracks()[0];
        const capabilities = track?.getCapabilities ? track.getCapabilities() : {};
        button?.classList.toggle("d-none", !capabilities.torch);
    },

    async _toggleTorch() {
        const track = this._stream?.getVideoTracks()[0];
        if (!track) {
            return;
        }
        const nextValue = !this._torchEnabled;
        try {
            await track.applyConstraints({ advanced: [{ torch: nextValue }] });
            this._torchEnabled = nextValue;
        } catch {
            this._setStatus("Este dispositivo no permite controlar la linterna.");
        }
    },

    _stopCamera() {
        if (this._scanTimer) {
            window.clearInterval(this._scanTimer);
            this._scanTimer = null;
        }
        for (const track of this._stream?.getTracks() || []) {
            track.stop();
        }
        this._stream = null;
        this._detector = null;
        this._torchEnabled = false;
        const video = this.el.querySelector(".kt_camera_website_video");
        if (video) {
            video.srcObject = null;
        }
    },

    _beep() {
        if (this.el.dataset.beep === "0") {
            return;
        }
        try {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            if (!AudioContext) {
                return;
            }
            const context = new AudioContext();
            const oscillator = context.createOscillator();
            const gain = context.createGain();
            oscillator.connect(gain);
            gain.connect(context.destination);
            oscillator.frequency.value = 880;
            gain.gain.value = 0.08;
            oscillator.start();
            window.setTimeout(() => {
                oscillator.stop();
                context.close();
            }, 120);
        } catch {
            // Audio is optional; a successful lookup must continue.
        }
    },
});

export default publicWidget.registry.KtCameraWebsiteBase;
