# Changelog — kt_toggle_override

## 19.0.1.0.3 (14/08/2026)

* **Fix de tests multi-compañía (nunca se habían corrido contra un
  Odoo real, ver CHECKLIST_MODULOS_ODOO.md §36):** `res.users.
  groups_id` → `group_ids` (rename real en la rama `19.0` de Odoo) +
  el usuario de prueba ahora incluye `stock.group_stock_user` (antes
  solo `base.group_user`, insuficiente para el ACL — el `AccessError`
  bloqueaba el `search()` antes de llegar a evaluar el `ir.rule` que
  el test decía probar). Ahora 100% verde (7 tests). Sin cambios de
  comportamiento del módulo — solo el test estaba mal construido.

## 19.0.1.0.2 (14/08/2026)

* **Aislamiento multi-compañía real (`ir.rule`):** `company_id` (vía
  `related='warehouse_id.company_id'`) no tenía ninguna `ir.rule` — un
  usuario con acceso a varias compañías podía ver/editar excepciones
  de características de bodegas de TODAS ellas al mismo tiempo. Nueva
  `security/kt_toggle_override_multi_company.xml` con dominio
  `[('company_id', 'in', company_ids)]`. Test de regresión agregado.

## 19.0.1.0.1 (14/08/2026)

* `kt_toggle_override.py`: `_sql_constraints` (deprecado en Odoo 19,
  no crea la restricción real en la base — `CHECKLIST_MODULOS_ODOO.md`
  §2.1) → `models.Constraint`. La restricción de una excepción única
  por bodega/característica ahora sí se aplica de verdad en Postgres.

## 19.0.1.0.0 (10/08/2026)

**Primera versión.**

* Modelo `kt.toggle.override`: excepción por bodega (`warehouse_id` +
  `toggle_key` + `value`) a los 5 interruptores de inventario de
  `kt_advanced_stock_flows` (`kt_restrict_lot_by_move`,
  `kt_auto_create_lot_on_receipt`, `kt_filter_lot_by_location`,
  `kt_lot_scrap_button`, `kt_no_negative_stock`).
* `res.company._kt_resolve_toggle(key, warehouse=None)`: resuelve el
  valor efectivo respetando primero la excepción de la bodega si
  existe, cayendo al valor de la compañía si no.
* Pestaña "Excepciones Kuvexta" en la ficha de bodega (Inventario →
  Configuración → Almacenes).
* Sin excepciones registradas, el comportamiento es idéntico a antes
  de instalar este módulo — puramente aditivo.
* `kt_advanced_stock_flows` 19.0.1.5.0 ya lo usa en sus 5 puntos de
  retrofit (ver el changelog de ese módulo).
* Diseño: `disenos_completos/kt_toggle_override/DISENO_ARQUITECTURA_
  KT_TOGGLE_OVERRIDE.md`.
