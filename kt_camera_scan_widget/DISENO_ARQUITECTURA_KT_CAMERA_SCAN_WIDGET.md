# Diseño de arquitectura — `kt_camera_scan_widget` ("ScanFlow Camera")

Estado: **implementado** — capa 1 (`BarcodeDetector` nativo), capa 2
(ZBar/WebAssembly vendorizado, `static/src/js/lib/`) y componente OWL
completos. Sin probar todavía en un dispositivo real, en particular
Safari/iOS con la capa 2 (ver sección 6 de `CHECKLIST_MODULOS_ODOO.md`).
Repositorio destino: `Kuvexta/odoo-community-tools`, rama `19.0`.
Licencia: LGPL-3 (código propio) + MIT (`@undecaf/barcode-detector-polyfill`
vendorizado) + LGPL-2.1+ (`@undecaf/zbar-wasm` vendorizado) — ver
`static/src/js/lib/*/LICENSE`.

## 1. El caso de uso que define el diseño

Un comprador de Kuvexta/SUBIENES está físicamente en la bodega de un
proveedor, sin lector de código de barras a la mano — solo su celular.
Necesita ir escaneando cada producto que va a comprar y que la orden de
compra se vaya armando sola, línea por línea, sin tocar el teclado y, en lo
posible, sin tener que mirar la pantalla entre escaneo y escaneo.

## 2. Qué SÍ hace este módulo (y qué no)

* **Sí**: captura el video de la cámara, decodifica el código, emite un
  evento con el valor decodificado, y da feedback (sonido/vibración) para
  poder escanear sin mirar la pantalla cada vez.
* **No**: no tiene lógica de negocio — no sabe qué es una orden de compra ni
  un producto. Eso vive en el módulo que lo consume (`kt_scanflow_documents`,
  y a futuro otros). Separación intencional: mismo widget reutilizable en
  Compras, Ventas, Facturas, y fuera del catálogo `kt_*` si se vende suelto.

## 3. Motor de decodificación — por capas, no una sola librería

Se evaluaron varias alternativas (ver tabla) antes de decidir la
arquitectura del motor:

| Opción | Rendimiento | Formatos | Compatibilidad | Mantenimiento |
|---|---|---|---|---|
| `BarcodeDetector` nativo | El más rápido — acelerado por hardware (ML Kit en Android) | EAN-13, UPC, Code128, QR, DataMatrix, PDF417 | Chrome/Edge (Android y escritorio). **Sin soporte en Safari/iOS** a mitad de 2026 | Nativo del navegador, sin mantenimiento propio |
| Quagga2 (lo que ya usa `ecommerce_barcode_search`) | Decodificación JS pura — más costo de CPU/batería en escaneo continuo | Solo 1D | Amplia, pero bug real documentado: falla al iniciar cámara en Samsung Galaxy S24/A54 tras actualización de Android | Mantenido por voluntarios (fork de QuaggaJS) |
| ZXing-js / html5-qrcode | Usa `BarcodeDetector` cuando está disponible, si no cae a JS puro | Más amplio que Quagga2 (incluye 2D) | Similar a Quagga2 | Ambos proyectos sin mantenedor activo actualmente |
| ZBar vía WebAssembly | Casi nativo — la mejor opción cuando no hay `BarcodeDetector` | 1D y 2D | Cualquier navegador con soporte WASM (prácticamente todos) | Depende del proyecto de compilación WASM elegido |
| Comerciales (Scandit, Dynamsoft) | El mejor medido en benchmarks | Amplio | Amplio | De pago — no encaja con el catálogo LGPL-3 |

**Decisión de diseño**: motor en cadena de capas —

1. Intentar `BarcodeDetector` nativo primero (rápido, sin descarga, no
   calienta el celular en sesiones largas de escaneo).
2. Si no está disponible (Safari/iOS), respaldo con **ZBar compilado a
   WebAssembly** — rendimiento cercano a nativo, cubre 1D y 2D.

Esto evita la dependencia de Quagga2 para este módulo nuevo, y evita también
el bug conocido de cámara en ciertos Samsung.

## 4. Componente OWL reutilizable

Un componente `CameraScanWidget` (OWL, framework de frontend de Odoo 19)
que:

1. Abre un modal con el feed de la cámara (`getUserMedia`).
2. Corre la cadena de decodificación descrita arriba sobre cada frame.
3. Al detectar un código válido, emite un evento (`onCodeDetected(code)`)
   hacia quien lo invocó.
4. Aplica un "cooldown" por código (~1.5 s) para no agregar el mismo
   producto varias veces si el código sigue en cuadro.
5. Da feedback de éxito (beep corto + `navigator.vibrate()` si el
   dispositivo lo soporta) y feedback distinto para código no reconocido,
   sin bloquear el bucle.

## 5. Manejo de condiciones reales de bodega

* **Poca luz**: si el navegador expone control de linterna
  (`MediaTrackConstraints` con `torch`), botón para activarla.
* **Códigos dañados/borrosos**: entrada manual como respaldo si tras varios
  segundos no decodifica nada.
* **Conexión inestable**: los códigos decodificados se agregan a una cola
  local en memoria del navegador antes de confirmarse contra el servidor —
  si la señal falla a mitad de sesión, no se pierde lo ya escaneado.

## 6. Interruptores de configuración (mínimos, es infraestructura)

| Campo (`res.company`) | Qué controla |
|---|---|
| `kt_camera_scan_enabled` | Si el botón de "escanear con cámara" aparece en los documentos que lo soportan |
| `kt_camera_scan_beep_enabled` | Si el sonido de confirmación está activo |
| `kt_camera_scan_default_facing` | Cámara trasera (`environment`, por defecto) vs frontal (`user`) |

## 7. Estructura de carpetas

```
kt_camera_scan_widget/
    __init__.py
    __manifest__.py         # depends: ['web']; assets en web.assets_backend
    static/
        src/
            js/
                camera_scan_widget.js     # componente OWL
                camera_scan_service.js    # cadena BarcodeDetector -> ZBar/WASM
            xml/
                camera_scan_widget.xml    # template OWL del modal
            scss/
                camera_scan_widget.scss
            lib/
                zbar-wasm/                # motor WASM vendorizado (@undecaf/zbar-wasm, LGPL-2.1+)
                barcode-detector-polyfill/ # envoltorio con la interfaz de BarcodeDetector (MIT)
    models/
        __init__.py
        res_company.py           # 3 campos de configuración
        res_config_settings.py
    views/
        res_config_settings_views.xml
    security/
        ir.model.access.csv
    i18n/
        es.po
    readme/
        DESCRIPTION.rst
        CONFIGURE.rst
        USAGE.rst
        ROADMAP.rst
    tests/
        __init__.py
        test_kt_camera_scan_widget.py
```

## 8. Relación con `ecommerce_barcode_search` / `kt_ecommerce_barcode_search_patch`

`ecommerce_barcode_search` (Cybrosys, AGPL-3, sin tocar) ya resuelve
escaneo por cámara para el **sitio web público**, con Quagga2 cargado por
CDN. Es un contexto distinto (visitante público, sin sesión, framework
`publicWidget`/jQuery) al de este módulo (backend autenticado, OWL) — no se
puede reutilizar el archivo JS tal cual, son paradigmas de frontend
distintos en Odoo.

**No se toca nada de `ecommerce_barcode_search` ni de su parche como parte
de este diseño.** Queda anotado en el `ROADMAP.rst` de ambos módulos como
consolidación opcional futura: que `kt_ecommerce_barcode_search_patch` deje
de mantener su propia copia de configuración de escaneo y en cambio consuma
la configuración compartida que viva en `kt_camera_scan_widget` — solo si
en el futuro conviene por mantenimiento, nunca como requisito de este
diseño.

## 9. Orden de implementación sugerido

1. `camera_scan_service.js` aislado — probar la cadena de decodificación
   (nativo → WASM) contra códigos reales, sin UI todavía.
2. Componente OWL del modal + feedback (beep/vibración).
3. Interruptores de configuración + panel de Ajustes.
4. Integración real con `kt_scanflow_documents` como primer consumidor.

## 10. Plan de pruebas

* Probar en al menos un dispositivo Android (Chrome, motor nativo) y, si es
  posible, un dispositivo iOS (Safari, motor WASM) — son rutas de código
  distintas, ambas deben probarse por separado.
* Probar específicamente con códigos EAN-13 reales de productos de Nexo
  Ferretero, en condiciones de luz variables.
* Confirmar el comportamiento de la linterna solo en dispositivos que
  realmente la soportan (`track.getCapabilities().torch`).
