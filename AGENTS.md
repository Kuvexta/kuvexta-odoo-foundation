# Agent rules — Kuvexta Odoo Foundation

- Target branch for Odoo 19 work: `19.0`.
- Keep this repository reusable by every higher layer.
- Never add dependencies on Professional, Community/AGPL, vendor-adapter, internal-only or unresolved-review modules.
- Preserve all third-party copyright and license notices.
- Do not copy purchased vendor source or AGPL implementation into Foundation.
- Prefer small, stable contracts and utilities over business-specific orchestration.
- Expected module license is LGPL-compatible unless a reviewed exception is documented.
- Physical migration must not change a module's license.
- Add/update tests when behavior changes and keep dependency boundaries machine-checkable.
