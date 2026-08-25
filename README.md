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
