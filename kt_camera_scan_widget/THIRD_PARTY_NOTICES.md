# Third-party notices — `kt_camera_scan_widget`

This Odoo addon contains Kuvexta code under LGPL-3 together with the following vendored third-party components. Their original license files are preserved next to the vendored files and remain authoritative.

## `@undecaf/barcode-detector-polyfill` v0.9.23

- Upstream package: `@undecaf/barcode-detector-polyfill`
- Version vendored: **0.9.23**
- License: **MIT**
- Copyright notice preserved in `static/src/js/lib/barcode-detector-polyfill/LICENSE`.
- Vendored files include `main.js` and the upstream `LICENSE`.
- Kuvexta modification: the upstream runtime import that referenced jsDelivr was changed to reference the locally vendored `zbar-wasm` package. The modification is documented in source/history and does not remove upstream notices.

## `@undecaf/zbar-wasm` v0.9.16

- Upstream package: `@undecaf/zbar-wasm`
- Version vendored: **0.9.16**
- License: **LGPL-2.1+**, as recorded in the module architecture/history; the full LGPL-2.1 license text is preserved in `static/src/js/lib/zbar-wasm/LICENSE`.
- Vendored files include `main.js`, `zbar.wasm`, and the upstream `LICENSE`.
- The compiled WebAssembly artifact remains third-party code and is not claimed as Kuvexta intellectual property.

## Provenance

The vendoring operation is recorded by source commit `60dd388e3ae082ba90cdb1c698e2f40cf3370fcb`, which documents the package versions, licenses, npm origin and the local-import modification.

## Distribution rule

Any distribution or repository migration of this addon must copy this notice together with both upstream license files and the corresponding vendored assets. The presence of these compatible open-source components does **not** change their ownership to Kuvexta.
