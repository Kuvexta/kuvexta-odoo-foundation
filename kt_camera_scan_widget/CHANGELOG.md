# Changelog — kt_camera_scan_widget

## 19.0.1.2.0 (06/08/2026)

* Puente website: `kt_camera_scan_website` (`auto_install`) integra
  este motor en `/shop` y en el layout público (botón flotante).
* Comparativa actualizada en `docs/COMPARATIVA_ESCANEO_CAMARA.md`.
* Help del toggle de compañía menciona backend + POS + website.

## 19.0.1.1.0 (06/08/2026)

* Fix `this.env._t` en control de linterna (mismo patrón Odoo 19 JS).
* Documentada comparativa vs `ecommerce_barcode_search` en
  `docs/COMPARATIVA_ESCANEO_CAMARA.md`.
* Integración POS movida al puente `kt_camera_scan_pos` (`auto_install`).
* ScanFlow ya consume este módulo vía import dinámico (botón cámara).

## 19.0.1.0.0 (05/08/2026)

Implementación inicial: motor BarcodeDetector → ZBar/WASM vendorizado,
diálogo OWL, toggles de compañía.
