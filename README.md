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

This repository has been initialized as part of the controlled split from `Kuvexta/odoo-community-tools`. Modules will only be moved after dependency, provenance and commercialization gates pass.
