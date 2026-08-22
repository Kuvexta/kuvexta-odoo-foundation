Módulo técnico sin modelos ni vistas propias: helpers de compatibilidad
que los 8 adaptadores de canal (``kt_marketplace_order_import``,
``_exito``, ``_rappi``, ``_falabella``, ``_pos_bridge``, ``_didifood``,
``_mercadolibre``, ``kt_payment_gateways``) usaban duplicados byte a
byte antes del 13/08/2026:

* ``apply_generic_core_jump(env)`` — alinea xmlids de una base que
  saltó de un núcleo pre-generalización (``kt.ml.*``) a los nombres
  genéricos actuales (``kt.marketplace.*``) sin esperar un ``-u``
  manual, y adopta el xmlid de un ``ir.cron`` cuando se movió de
  módulo al extraerse un adaptador a módulo propio.
* ``purge_stale_extracted_core_views(env)`` — purga vistas huérfanas
  de esa misma migración que violan el ``CHECK`` de herencia de
  vistas de Odoo 19 y abortan cualquier Instalar/Actualizar.

Ningún módulo de negocio depende de este para funcionar — es
infraestructura interna para no repetir el mismo código (y el mismo
riesgo de que un fix se aplique en 7 de 8 copias) en cada adaptador.

Ver diseño completo:
``disenos_completos/kt_marketplace_cross_cutting/
16_KT_MARKETPLACE_CORE_UTILS_HOOKS_COMPARTIDOS.md``.
