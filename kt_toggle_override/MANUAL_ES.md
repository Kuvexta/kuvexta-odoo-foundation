# Manual operativo — KT Toggle Override

## Propósito

Define excepciones por bodega para interruptores consumidos por flujos de stock.
Es Foundation y no depende del módulo Professional que pueda interpretar esas
excepciones.

## Configuración y uso

En Inventario abra la bodega y configure únicamente las excepciones necesarias.
Valide la empresa activa y documente el motivo operacional. Sin un consumidor
compatible, guardar una excepción no cambia por sí solo el flujo de inventario.
Consulte `readme/CONFIGURE.rst` y `readme/USAGE.rst`.

## Controles

Pruebe bodega sin excepción, excepción explícita, multiempresa y actualización
desde la versión instalada. Evite valores globales que oculten políticas por
establecimiento.

Código/manual: `Kuvexta/kuvexta-odoo-foundation@19.0`; decisiones de diseño:
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
