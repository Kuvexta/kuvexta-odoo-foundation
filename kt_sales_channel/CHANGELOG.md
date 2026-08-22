# Changelog — kt_sales_channel

## 19.0.1.3.4 (14/08/2026)

* **Fix de tests multi-compañía (nunca se habían corrido contra un
  Odoo real, ver CHECKLIST_MODULOS_ODOO.md §36):** `res.users.
  groups_id` → `group_ids` (rename real en la rama `19.0` de Odoo) +
  el usuario de prueba ahora incluye `sales_team.group_sale_salesman`
  (antes solo `base.group_user`, insuficiente para el ACL — el
  `AccessError` bloqueaba el `search()` antes de llegar a evaluar el
  `ir.rule` que el test decía probar). Ahora 100% verde (13 tests).
  Sin cambios de comportamiento del módulo — solo el test estaba mal
  construido.

## 19.0.1.3.3 (14/08/2026)

* **Aislamiento multi-compañía real (`ir.rule`):** `company_id` es
  opcional ("vacío = disponible en todas las compañías"), pero hasta
  esta versión no había ninguna `ir.rule` — un canal atado a una
  compañía puntual podía verse/editarse desde OTRA compañía. Nueva
  `security/kt_sales_channel_multi_company.xml` con el mismo patrón
  "compartido si está vacío" que `kt_product_multi_barcode`. Tests de
  regresión agregados (canal global sigue visible; canal de una
  compañía se aísla).

## 19.0.1.3.2 (14/08/2026)

* `kt_sales_channel.py`: `_sql_constraints` (deprecado en Odoo 19, no
  crea la restricción real en la base — `CHECKLIST_MODULOS_ODOO.md`
  §2.1) → `models.Constraint`. La restricción de código de canal
  único ahora sí se aplica de verdad en Postgres.

## 19.0.1.3.1 (13/08/2026)

* `views/kt_sales_channel_views.xml`: en Odoo 19 `<group>` dentro de
  una vista `search` ya no acepta `expand`/`string` (validación RNG
  más estricta). Bloqueaba Instalar/Actualizar de este módulo.
  Detalle en `CHECKLIST_MODULOS_ODOO.md` §3.12.

## 19.0.1.3.0 (11/08/2026)

* Nuevos módulos hermanos publicados en paralelo: `kt_marketplace_falabella`
  y `kt_marketplace_rappi` (P0). Sin cambios de modelo en este módulo —
  ambos reusan `kt.sales.channel`/`business_vertical` tal cual.

## 19.0.1.2.0 (10/08/2026)

* Deep-link a Mercado Libre desde el canal, logo por canal (`image_128`)
  y soporte de respuestas frecuentes (doc 11 §7.5/§7.6/§7.8).

## 19.0.1.1.0 (10/08/2026)

* Centro de atención (dashboard) — primeras tarjetas de resumen.
* `responsible_user_id` por canal (doc 11 §7.1/§7.4) — base para todas
  las notificaciones activas configurables por canal en módulos
  posteriores (`kt_marketplace_order_import`, `kt_packing_station`).

## 19.0.1.0.2 (08/08/2026)

* Fix: no truncar los campos de `pos.config` al abrir el Punto de Venta.

## 19.0.1.0.1 (07/08/2026)

* Fix: canales Facebook/TikTok/Homecenter quedan como `channel_type`
  manual (no se confundían con canales con adaptador propio).

## 19.0.1.0.0 (07/08/2026)

**Primera versión.**

* Modelo `kt.sales.channel` — catálogo único y transversal de canales de
  venta (Mercado Libre, Éxito, Falabella, Rappi, DiDi Food, Facebook,
  TikTok, Homecenter, manual) con `code`, `channel_type`,
  `business_vertical` (retail/food_delivery/ambos) y `image_128`.
* `kt.marketplace.notification` — cola compartida de eventos entrantes
  (webhooks/polling) de cualquier canal, reusada por todos los
  adaptadores.
* Núcleo compartido base para `kt_marketplace_order_import` y los
  adaptadores que se construyeron después.
