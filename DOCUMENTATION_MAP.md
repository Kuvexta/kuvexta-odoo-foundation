# Mapa de documentación — Foundation

## Ruta rápida

- Inventario físico y procedencia: `MIGRATION_MANIFEST.json` y receipts raíz.
- Código, operación y soporte: `/<addon>/README.rst`, `MANUAL_ES.md`,
  `CHANGELOG.md`, pruebas y fragmentos `readme/`.
- Políticas/diseños/FAQ/PQR/lecciones comunes: repositorio privado
  `Kuvexta/kuvexta-odoo-knowledge`, empezando por `INDEX.yaml`.
- Bundle instalable, promoción y rollback: `Kuvexta/kuvexta-odoo-integration`.
- Clasificación y procedencia histórica: `Kuvexta/odoo-community-tools`.

Foundation solo admite contratos reutilizables y neutrales. Un diseño que
requiera Professional, Community, Vendor o Internal se coloca en una capa
superior o en un bridge explícito. Las copias de Source no reciben mejoras.
