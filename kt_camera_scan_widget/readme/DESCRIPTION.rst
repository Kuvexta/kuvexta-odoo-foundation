Infraestructura compartida de escaneo por cámara para el backend de Odoo
(**ScanFlow Camera**) — sin necesidad de un lector físico de código de
barras.

Usa la API nativa ``BarcodeDetector`` del navegador cuando está disponible
(la más rápida, acelerada por hardware), y cae a un motor ZBar compilado a
WebAssembly cuando no lo está (por ejemplo, Safari/iOS).

Este módulo no tiene lógica de negocio propia: expone un componente
reutilizable que otros módulos (como ``kt_scanflow_documents``) consumen
para ofrecer captura por cámara además del lector físico tradicional.

Pensado especialmente para compradores en bodega de proveedor: escaneo
continuo con feedback sonoro/vibración, sin necesidad de mirar la pantalla
entre producto y producto, y con linterna disponible en dispositivos que la
soportan.

**Licencias de terceros vendorizadas** (``static/src/js/lib/``, descargadas
del registro oficial de npm, nunca desde un CDN en producción): el motor
WebAssembly ``@undecaf/zbar-wasm`` (LGPL-2.1+) y el envoltorio
``@undecaf/barcode-detector-polyfill`` (MIT) que expone la misma interfaz
que ``BarcodeDetector`` nativo. Ver el archivo ``LICENSE`` dentro de cada
subcarpeta de ``lib/`` para el texto completo.
