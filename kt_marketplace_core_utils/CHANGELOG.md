# Changelog — kt_marketplace_core_utils

## 19.0.1.0.2 (18/08/2026)

* **Bug funcional real corregido — `_auto_init_marketplace_models`
  (llamada desde `apply_generic_core_jump`, en el `pre_init_hook` de
  cualquier adaptador de canal) fallaba en silencio para TODO modelo
  `kt.marketplace.*` con una relación `Many2one`/`Many2many`**, y
  llegó a hacer fallar por completo el job `odoo-tests` del CI real
  (ver `CHECKLIST_MODULOS_ODOO.md` §51): llamaba a `model._auto_init()`
  directo, fuera de una llamada activa a `Registry.init_models()` —
  eso revienta con `AttributeError: 'Registry' object has no attribute
  '_post_init_queue'` porque ese atributo es TRANSITORIO (Odoo lo crea
  y borra dentro de `init_models()`), y varios `Field._auto_init()`
  del núcleo (relaciones, en particular) esperan que exista. El
  `try/except` que envolvía la llamada lo capturaba como warning, así
  que el `_auto_init()` real quedaba SIN EJECUTAR para esos modelos —
  el propósito del hook (crear/actualizar la tabla sin esperar el
  próximo `-u`) simplemente no se cumplía para ningún modelo con
  relaciones. Corregido: usar `env.registry.init_models(cr,
  [model_name], {})` en vez de `model._auto_init()` directo — es la
  API pública de Odoo para esto, que crea/borra `_post_init_queue` (y
  el resto de los atributos transitorios) por su cuenta antes/después
  de llamar a `_auto_init()`, así que ya no puede reventar por este
  motivo.

## 19.0.1.0.1 (15/08/2026)

* **Bug funcional real corregido — el más serio encontrado en toda la
  serie de rondas de investigación de tests (ver CHECKLIST_MODULOS_
  ODOO.md §37, séptima ronda):** `apply_generic_core_jump` (llamado
  desde el `pre_init_hook` de cualquier adaptador de canal — Éxito,
  Rappi, Falabella, DiDi Food, Mercado Libre, pos_bridge, `kt_payment_
  gateways`) recarga el XML/CSV completo de `kt_marketplace_order_
  import`/`_feed_sync` (`_reload_core_data_files`, `convert_file(...,
  mode='update')`). Eso RE-APLICA el `parent_id`/`sequence` declarado
  en el XML de sus menús — DESHACIENDO en silencio el reparenting que
  `kt_marketplace_console.hooks.reparent_console_menus()` ya había
  aplicado al instalarse. Pasaba cada vez que se instalaba/actualizaba
  CUALQUIER adaptador de canal DESPUÉS de que `kt_marketplace_console`
  ya estuviera instalado — reproducido instalando `kt_marketplace_
  mercadolibre` sobre una base con `order_import`+`console` ya
  instalados: el menú "Solicitudes" volvía a su ubicación genérica.
  Nuevo `_reapply_console_menu_reparenting()`: re-aplica el
  reparenting de `console` al final de `apply_generic_core_jump`
  (import perezoso, sin dependencia dura — no-op si `console` no está
  instalado). Antes solo existía `detect_misplaced_console_menus()`
  (wizard de Mantenimiento) para DETECTAR este caso, sin corregirlo
  automáticamente.
* `_reload_core_data_files`: ahora verifica que el módulo esté
  REALMENTE instalado (`ir.module.module.state == 'installed'`), no
  solo que su carpeta exista en el `addons_path` — sin este chequeo,
  llamar a este hook compartido sin `kt_marketplace_order_import`/
  `_feed_sync` instalados (nunca pasa hoy, pero el hook no debería
  asumirlo) fallaba con `NotNullViolation` al recargar `ir.model.
  access.csv` contra modelos que no existen en el registry.
* Fixes de test: `test_alias_xmlid_renames_when_new_missing` esperaba
  que el xmlid viejo dejara de "existir" tras un rename — pero
  `_alias_xmlid` renombra IN PLACE (mismo `id`), así que la fila SIGUE
  existiendo (solo cambia el `name`); corregida la aserción para
  verificar lo que realmente importa (ya no hay ningún xmlid con el
  nombre viejo bajo ese módulo). `test_hooks_stale_views.py`: el
  `UPDATE` crudo de `arch_db` no era compatible con builds donde esa
  columna es `jsonb` — mismo fix de tipo de columna aplicado en varios
  módulos esta semana. 100% verde (11/11 tests), se suma a `MODULES_
  VERIFIED` del CI (no estaba en ninguna de las dos listas hasta
  ahora).

## 19.0.1.0.0 (13/08/2026)

* Módulo nuevo: extrae `hooks_core_jump.py`/`hooks_stale_views.py`,
  que hasta hoy vivían copiados byte a byte idénticos en 8 módulos
  (`kt_marketplace_order_import`, `_exito`, `_rappi`, `_falabella`,
  `_pos_bridge`, `_didifood`, `_mercadolibre`, `kt_payment_gateways`),
  a un único módulo compartido. Motivado por un incidente real
  (`gc`, 13/08/2026): un bug en ese archivo tuvo que arreglarse 8
  veces a mano, y una de las copias (`kt_marketplace_mercadolibre`)
  quedó desincronizada por no estar desplegada en ese momento.
* `apply_generic_core_jump`: agrega adopción de xmlid de `ir.cron`
  cuando cambió de módulo al extraerse un adaptador (cubre el cron
  `ir_cron_kt_ml_poll_orders` y sus 7 hermanos, huérfanos bajo
  `kt_marketplace_order_import` desde la extracción de Mercado Libre
  el 12/08/2026 — `CHECKLIST_MODULOS_ODOO.md` §3.13).
* Ver diseño completo:
  `disenos_completos/kt_marketplace_cross_cutting/
  16_KT_MARKETPLACE_CORE_UTILS_HOOKS_COMPARTIDOS.md`.
