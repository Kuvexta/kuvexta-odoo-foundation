# Manual operativo — KT Sales Channel

## Propósito

Identifica el canal de venta en pedidos manuales, integrados y POS, con reporte
por canal y aislamiento multiempresa.

## Configuración y uso

Instale el addon, configure los canales permitidos y asigne el canal por defecto
cuando corresponda. En ventas y POS confirme que los pedidos reciben el canal
esperado y que los reportes respetan empresa, fechas y permisos. Las instrucciones
detalladas están en `readme/CONFIGURE.rst` y `readme/USAGE.rst`.

## Actualización

Pruebe pedidos históricos, creación manual, flujo POS e integraciones de
marketplace. No elimine XML IDs ni tipos usados por otros addons sin migración y
ensayo conjunto.

Código/manual: `Kuvexta/kuvexta-odoo-foundation@19.0`; arquitectura y mejoras:
`Kuvexta/kuvexta-odoo-knowledge`.
## Autoridad documental y mejora continua

- Código y operación de este addon: `Kuvexta/kuvexta-odoo-foundation@19.0`.
- Investigación, diseños, FAQ/PQR, incidentes y lecciones transversales:
  `Kuvexta/kuvexta-odoo-knowledge` mediante `INDEX.yaml` y `CATALOG.yaml`.
- Composición instalable y rollback: bundle exacto de
  `Kuvexta/kuvexta-odoo-integration`.

La copia retenida en Source es evidencia congelada. Toda mejora se propone aquí
y debe actualizar manual, pruebas y comprobante del árbol cuando corresponda.
Los ensayos externos aplicables no se consideran cerrados por una prueba local.
