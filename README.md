# Kuvexta Odoo Foundation

Reusable foundation modules, contracts and shared infrastructure for Kuvexta on Odoo Community.

## Scope

This repository is the lowest reusable layer in the Kuvexta Odoo architecture. Code placed here must remain independent from Professional, Community/AGPL, vendor-purchased and internal-only layers.

## Branch policy

- `main`: repository governance and cross-version documentation.
- `19.0`: Odoo 19 code line.

## Licensing

Licensing is declared per Odoo module. A repository-level assumption must never override a module manifest or third-party notice. Foundation modules are expected to be LGPL-compatible unless an explicit reviewed exception is documented.

## Migration status

`MIGRATION_MANIFEST.json` is the authoritative physical inventory. Every addon
present here passed dependency/provenance gates and has an exact-tree receipt.
The camera Website base is intentionally limited to official product barcodes;
its multi-barcode integration lives as an explicit bridge in Professional.

## Ruta documental unificada

Consulte [DOCUMENTATION_MAP.md](DOCUMENTATION_MAP.md). Las políticas,
investigaciones, diseños de módulos/ecosistemas, FAQ/PQR, incidentes y lecciones
transversales se mantienen en el repositorio privado
Kuvexta/kuvexta-odoo-knowledge, empezando por INDEX.yaml. Este repositorio
conserva la documentación operativa y evidencia que corresponden a su propio rol.
