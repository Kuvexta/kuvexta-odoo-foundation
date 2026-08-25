# Manual operativo — KT Payment Gateway Core

## Propósito

Contratos neutrales para encadenar adaptadores de pago sobre ventas. No procesa
transacciones, comisiones, retenciones, conciliaciones ni credenciales.

## Instalación y actualización

Instale el addon como dependencia Foundation. No crea un proveedor de pago por sí
solo y no requiere configuración. Tras actualizar, instale o actualice en staging
cada consumidor y pruebe creación/confirmación de pedidos sin pasarela y con cada
adaptador admitido.

## Límite de soporte

La operación financiera pertenece a `kt_payment_operations`; Mercado Pago usa el
proveedor oficial de Odoo mediante su bridge Professional. Credenciales,
webhooks y conciliación real siguen siendo gates externos.

Código/manual: `Kuvexta/kuvexta-odoo-foundation@19.0`. Diseños y FAQ
transversales: `Kuvexta/kuvexta-odoo-knowledge`.
## Autoridad documental y mejora continua

- Código y operación de este addon: `Kuvexta/kuvexta-odoo-foundation@19.0`.
- Investigación, diseños, FAQ/PQR, incidentes y lecciones transversales:
  `Kuvexta/kuvexta-odoo-knowledge` mediante `INDEX.yaml` y `CATALOG.yaml`.
- Composición instalable y rollback: bundle exacto de
  `Kuvexta/kuvexta-odoo-integration`.

La copia retenida en Source es evidencia congelada. Toda mejora se propone aquí
y debe actualizar manual, pruebas y comprobante del árbol cuando corresponda.
Los ensayos externos aplicables no se consideran cerrados por una prueba local.
