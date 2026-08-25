# Manual operativo — KT Marketplace Core Utils

## Propósito

Biblioteca Foundation con utilidades de compatibilidad compartidas por los
adaptadores de marketplace. No ofrece menú ni operación directa al usuario.

## Instalación y operación

Se instala como dependencia de los módulos que usan sus contratos. No requiere
credenciales ni configuración manual. Antes de actualizar, pruebe en staging la
instalación y actualización de todos los consumidores, porque una utilidad común
puede afectar varios canales aunque este addon no tenga interfaz.

Consulte `readme/DESCRIPTION.rst`, `readme/CONFIGURE.rst`, `readme/USAGE.rst` y
`readme/ROADMAP.rst` para el contrato vigente.

## Soporte

No coloque lógica específica de un proveedor en esta capa. Los diseños comunes y
lecciones viven en `Kuvexta/kuvexta-odoo-knowledge`; la implementación es
autoridad de `Kuvexta/kuvexta-odoo-foundation@19.0`.
## Autoridad documental y mejora continua

- Código y operación de este addon: `Kuvexta/kuvexta-odoo-foundation@19.0`.
- Investigación, diseños, FAQ/PQR, incidentes y lecciones transversales:
  `Kuvexta/kuvexta-odoo-knowledge` mediante `INDEX.yaml` y `CATALOG.yaml`.
- Composición instalable y rollback: bundle exacto de
  `Kuvexta/kuvexta-odoo-integration`.

La copia retenida en Source es evidencia congelada. Toda mejora se propone aquí
y debe actualizar manual, pruebas y comprobante del árbol cuando corresponda.
Los ensayos externos aplicables no se consideran cerrados por una prueba local.
