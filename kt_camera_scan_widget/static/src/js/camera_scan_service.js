/** @odoo-module **/

/**
 * Cadena de decodificación de códigos de barras/QR, por capas — ver
 * DISENO_ARQUITECTURA_KT_CAMERA_SCAN_WIDGET.md, sección 3.
 *
 * Capa 1: `BarcodeDetector` nativo del navegador (Chrome/Edge en
 *         Android y escritorio; acelerado por hardware). Cubre la
 *         gran mayoría de los dispositivos reales usados por
 *         compradores/operarios de Kuvexta.
 * Capa 2: respaldo ZBar compilado a WebAssembly
 *         (`static/src/js/lib/zbar-wasm/`, paquete
 *         `@undecaf/zbar-wasm` v0.9.16, LGPL-2.1+) envuelto con la
 *         misma interfaz que `BarcodeDetector`
 *         (`static/src/js/lib/barcode-detector-polyfill/`, paquete
 *         `@undecaf/barcode-detector-polyfill` v0.9.23, MIT) —
 *         ambos VENDORIZADOS localmente (descargados del registro
 *         oficial de npm, nunca cargados desde un CDN en tiempo de
 *         ejecución; ver el comentario de parche dentro de
 *         `lib/barcode-detector-polyfill/main.js` para el único
 *         cambio hecho sobre el código original). Cubre Safari/iOS y
 *         cualquier otro navegador sin `BarcodeDetector` nativo.
 *
 * Se carga con `import()` dinámico (no en el bundle de assets de
 * Odoo) a propósito: son ~250 KB de WebAssembly que la mayoría de los
 * usuarios (Chrome/Android, con capa 1 disponible) nunca necesita
 * descargar. Al ser un `import()` de una URL de archivo estático real
 * (no del bundle concatenado), la resolución interna de
 * `import.meta.url` que usa el cargador WASM para encontrar
 * `zbar.wasm` junto a `main.js` sigue funcionando sin cambios.
 *
 * Esta capa NO tiene lógica de negocio ni sabe nada de Odoo — solo
 * decodifica frames de video y devuelve el texto crudo detectado.
 */

/**
 * @returns {boolean} si el navegador actual expone `BarcodeDetector`
 * nativo (Chrome/Edge en Android y escritorio con ML Kit).
 */
export function hasNativeBarcodeDetector() {
    return typeof window !== "undefined" && "BarcodeDetector" in window;
}

// Formatos que interesa reconocer en documentos/inventario de
// Kuvexta. `data_matrix` y `pdf417` solo los soporta la capa 1
// (BarcodeDetector nativo) — ZBar (capa 2) no los implementa, ver
// `ZBAR_SUPPORTED_FORMATS` más abajo.
const NATIVE_SUPPORTED_FORMATS = [
    "ean_13", "ean_8", "upc_a", "upc_e", "code_128", "code_39",
    "itf", "qr_code", "data_matrix", "pdf417",
];

// Subconjunto realmente soportado por @undecaf/zbar-wasm (verificado
// contra `lib/barcode-detector-polyfill/main.js`, la lista de
// `r.register(...)` de formatos registrados).
const ZBAR_SUPPORTED_FORMATS = [
    "ean_13", "ean_8", "upc_a", "upc_e", "code_128", "code_39",
    "itf", "qr_code",
];

const ZBAR_POLYFILL_URL = "/kt_camera_scan_widget/static/src/js/lib/barcode-detector-polyfill/main.js";

/**
 * Envuelve `BarcodeDetector` nativo en una interfaz mínima y estable
 * (`detect(videoOrCanvasEl)` -> Promise<string[]>), para que el
 * componente que la usa no necesite conocer la API exacta del
 * navegador ni sus diferencias de formatos soportados.
 */
export class NativeBarcodeDetectorEngine {
    constructor() {
        this._detector = new window.BarcodeDetector({ formats: NATIVE_SUPPORTED_FORMATS });
    }

    async detect(source) {
        const results = await this._detector.detect(source);
        return results.map((r) => r.rawValue).filter(Boolean);
    }
}

/**
 * Misma interfaz que `NativeBarcodeDetectorEngine`, respaldada por
 * ZBar/WebAssembly en vez del `BarcodeDetector` nativo del navegador
 * — `BarcodeDetectorPolyfill.detect()` ya devuelve objetos con la
 * misma forma (`{rawValue, format, ...}`) que la API nativa, por
 * diseño del propio paquete (es un polyfill de esa API exacta).
 */
export class ZbarWasmEngine {
    constructor(BarcodeDetectorPolyfill) {
        this._detector = new BarcodeDetectorPolyfill({ formats: ZBAR_SUPPORTED_FORMATS });
    }

    async detect(source) {
        const results = await this._detector.detect(source);
        return results.map((r) => r.rawValue).filter(Boolean);
    }
}

async function createZbarWasmEngine() {
    const module = await import(ZBAR_POLYFILL_URL);
    return new ZbarWasmEngine(module.BarcodeDetectorPolyfill);
}

/**
 * Punto único de creación del motor de decodificación disponible.
 * Devuelve `null` si ninguna capa está disponible/utilizable en este
 * navegador (el componente debe caer a entrada manual en ese caso).
 *
 * Es asíncrona porque la capa 2 (ZBar/WASM) se carga con `import()`
 * dinámico bajo demanda — nunca se descarga si el navegador ya tiene
 * `BarcodeDetector` nativo.
 */
export async function createBarcodeEngine() {
    if (hasNativeBarcodeDetector()) {
        try {
            return new NativeBarcodeDetectorEngine();
        } catch {
            // Sigue intentando con la capa 2 antes de rendirse.
        }
    }
    try {
        return await createZbarWasmEngine();
    } catch {
        // Navegador sin soporte de WebAssembly, o el archivo vendorizado
        // no se pudo cargar (ej. instalación con solo minificado activo
        // y una ruta de assets distinta) — se cae a entrada manual.
        return null;
    }
}
