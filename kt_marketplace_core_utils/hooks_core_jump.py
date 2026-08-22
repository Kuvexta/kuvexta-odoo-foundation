# -*- coding: utf-8 -*-
# Copyright 2026 Kuvexta
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
"""Salto 19.0.1.5.5 → xmlids/modelos genéricos sin esperar el ``-u``.

Cubre: cron ML (``model_kt_ml_question``) y vistas posteriores a 1.5.5
(``view_kt_marketplace_location_map_list``, pos_bridge/DiDi 16:05 GMT).
Recarga TODO el data XML/CSV actual de order_import y feed_sync.

Hasta el 13/08/2026 este archivo vivía copiado byte a byte idéntico en
8 módulos (``kt_marketplace_order_import``, ``_exito``, ``_rappi``,
``_falabella``, ``_pos_bridge``, ``_didifood``, ``_mercadolibre``,
``kt_payment_gateways``) — un bug real (``load_information_from_
description_file`` eliminada en Odoo 19) tuvo que arreglarse en las 8
copias a mano, con el riesgo real de que alguna quedara
desincronizada (pasó: ``kt_marketplace_mercadolibre`` no se arregló
en la primera pasada porque ni estaba desplegado). Ver diseño
completo: ``disenos_completos/kt_marketplace_cross_cutting/
16_KT_MARKETPLACE_CORE_UTILS_HOOKS_COMPARTIDOS.md``.
"""
import logging

from odoo.modules.module import get_module_path

_logger = logging.getLogger(__name__)

_MODEL_RENAMES = (
    ("kt.ml.product.binding", "kt.marketplace.product.binding"),
    ("kt.ml.question", "kt.marketplace.question"),
    ("kt.ml.claim", "kt.marketplace.claim"),
    ("kt.ml.category.map", "kt.marketplace.category.map"),
)

_XMLID_RENAMES = (
    (
        "kt_marketplace_order_import",
        "model_kt_ml_question",
        "model_kt_marketplace_question",
    ),
    ("kt_marketplace_order_import", "model_kt_ml_claim", "model_kt_marketplace_claim"),
    (
        "kt_marketplace_order_import",
        "model_kt_ml_product_binding",
        "model_kt_marketplace_product_binding",
    ),
    (
        "kt_marketplace_feed_sync",
        "model_kt_ml_category_map",
        "model_kt_marketplace_category_map",
    ),
    (
        "kt_marketplace_order_import",
        "view_kt_ml_question_list",
        "view_kt_marketplace_question_list",
    ),
    (
        "kt_marketplace_order_import",
        "view_kt_ml_question_form",
        "view_kt_marketplace_question_form",
    ),
    (
        "kt_marketplace_order_import",
        "view_kt_ml_question_search",
        "view_kt_marketplace_question_search",
    ),
    (
        "kt_marketplace_order_import",
        "view_kt_ml_product_binding_list",
        "view_kt_marketplace_product_binding_list",
    ),
    (
        "kt_marketplace_order_import",
        "view_kt_ml_product_binding_form",
        "view_kt_marketplace_product_binding_form",
    ),
    (
        "kt_marketplace_order_import",
        "view_kt_ml_product_binding_search",
        "view_kt_marketplace_product_binding_search",
    ),
    (
        "kt_marketplace_order_import",
        "view_kt_ml_claim_list",
        "view_kt_marketplace_claim_list",
    ),
    (
        "kt_marketplace_order_import",
        "view_kt_ml_claim_form",
        "view_kt_marketplace_claim_form",
    ),
    (
        "kt_marketplace_feed_sync",
        "view_kt_ml_category_map_list",
        "view_kt_marketplace_category_map_list",
    ),
    (
        "kt_marketplace_feed_sync",
        "view_kt_ml_category_map_form",
        "view_kt_marketplace_category_map_form",
    ),
    (
        "kt_marketplace_order_import",
        "action_kt_ml_product_binding",
        "action_kt_marketplace_product_binding",
    ),
    (
        "kt_marketplace_order_import",
        "menu_kt_ml_product_binding",
        "menu_kt_marketplace_product_binding",
    ),
    (
        "kt_marketplace_order_import",
        "action_kt_ml_question",
        "action_kt_marketplace_question",
    ),
    (
        "kt_marketplace_order_import",
        "menu_kt_ml_question",
        "menu_kt_marketplace_question",
    ),
    (
        "kt_marketplace_order_import",
        "action_kt_ml_claim",
        "action_kt_marketplace_claim",
    ),
    ("kt_marketplace_order_import", "menu_kt_ml_claim", "menu_kt_marketplace_claim"),
    (
        "kt_marketplace_feed_sync",
        "action_kt_ml_category_map",
        "action_kt_marketplace_category_map",
    ),
    (
        "kt_marketplace_feed_sync",
        "menu_kt_ml_category_map",
        "menu_kt_marketplace_category_map",
    ),
)

_CORE_MODULES = (
    "kt_marketplace_order_import",
    "kt_marketplace_feed_sync",
)

# gc 13/08/2026 23:00 GMT: al extraer Mercado Libre a módulo propio
# (12/08/2026), estos 8 crons se movieron de archivo/módulo pero
# conservaron el mismo id técnico (mismo patrón que las vistas/
# acciones de _XMLID_RENAMES, salvo que acá también cambia el
# MÓDULO, no solo el nombre). Una base que instaló el núcleo viejo
# pero nunca instaló ``kt_marketplace_mercadolibre`` se queda con el
# xmlid apuntando al módulo de antes de la extracción — y si algún
# día instala el adaptador ML sin que nadie "adopte" el xmlid viejo,
# el cron sigue corriendo con el código viejo (ya extraído) y falla
# con ``AttributeError`` (visto real en gc: ``kt_ml_poll_orders``).
_CRON_MODULE_MIGRATIONS = (
    (
        "kt_marketplace_order_import",
        "ir_cron_kt_ml_poll_orders",
        "kt_marketplace_mercadolibre",
    ),
    (
        "kt_marketplace_order_import",
        "ir_cron_kt_ml_refresh_tokens",
        "kt_marketplace_mercadolibre",
    ),
    (
        "kt_marketplace_order_import",
        "ir_cron_kt_ml_resync_status",
        "kt_marketplace_mercadolibre",
    ),
    (
        "kt_marketplace_order_import",
        "ir_cron_kt_ml_question_sla",
        "kt_marketplace_mercadolibre",
    ),
    (
        "kt_marketplace_order_import",
        "ir_cron_kt_ml_feed_stock_price",
        "kt_marketplace_mercadolibre",
    ),
    (
        "kt_marketplace_order_import",
        "ir_cron_kt_ml_category_attributes",
        "kt_marketplace_mercadolibre",
    ),
    (
        "kt_marketplace_order_import",
        "ir_cron_kt_ml_health_check",
        "kt_marketplace_mercadolibre",
    ),
    (
        "kt_marketplace_order_import",
        "ir_cron_kt_ml_ads_sync",
        "kt_marketplace_mercadolibre",
    ),
)


def apply_generic_core_jump(env):
    """Idempotente: no-op si gc ya saltó (xmlids nuevos presentes)."""
    _try_rename_models(env)
    for module, old_name, new_name in _XMLID_RENAMES:
        _alias_xmlid(env.cr, module, old_name, new_name)
    for old_module, name, new_module in _CRON_MODULE_MIGRATIONS:
        _adopt_cross_module_xmlid(env.cr, old_module, name, new_module)
    _reload_core_data_files(env)
    _auto_init_marketplace_models(env)
    _reapply_console_menu_reparenting(env)
    invalidate = getattr(env, "invalidate_all", None)
    if invalidate:
        invalidate()
    clearer = getattr(env.registry, "clear_cache", None) or getattr(
        env.registry, "clear_all_caches", None
    )
    if clearer:
        try:
            clearer()
        except TypeError:
            try:
                clearer("default")
            except Exception:
                pass


def _try_rename_models(env):
    try:
        import importlib.util

        module_path = get_module_path("kt_product_multi_barcode")
        if not module_path:
            return
        path = module_path + "/migrations/nexo_upgrade.py"
        spec = importlib.util.spec_from_file_location("nexo_upgrade_core_jump", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if not hasattr(mod, "rename_model"):
            return
        for old_name, new_name in _MODEL_RENAMES:
            mod.rename_model(env.cr, old_name, new_name)
    except Exception:
        _logger.warning("hooks_core_jump: rename_model skipped", exc_info=True)


def _alias_xmlid(cr, module, old_name, new_name):
    """Renombra el xmlid ``module.old_name`` a ``module.new_name`` (mismo módulo)."""
    cr.execute(
        """
        SELECT id, model, res_id FROM ir_model_data
         WHERE module = %s AND name = %s
        """,
        (module, old_name),
    )
    old = cr.fetchone()
    cr.execute(
        """
        SELECT id FROM ir_model_data
         WHERE module = %s AND name = %s
        """,
        (module, new_name),
    )
    new = cr.fetchone()
    if old and not new:
        cr.execute(
            "UPDATE ir_model_data SET name = %s WHERE id = %s",
            (new_name, old[0]),
        )
        _logger.info("hooks_core_jump: xmlid %s.%s → %s", module, old_name, new_name)
        return
    if old and new:
        cr.execute("DELETE FROM ir_model_data WHERE id = %s", (old[0],))


def _adopt_cross_module_xmlid(cr, old_module, name, new_module):
    """Adopta ``old_module.name`` (de antes de una extracción) como
    ``new_module.name``.

    A diferencia de ``_alias_xmlid`` (mismo módulo, otro nombre), esto
    cubre el caso de un registro (típicamente ``ir.cron``) que cambió
    de MÓDULO al extraerse un adaptador a un módulo propio. Si el
    módulo nuevo todavía no está instalado en esta base, no hace
    nada (no hay nada que "adoptar" hasta que ese módulo cree su
    propia fila) — se vuelve a intentar la próxima vez que corra este
    hook, sin efecto si ya se resolvió.
    """
    cr.execute(
        "SELECT id FROM ir_model_data WHERE module = %s AND name = %s",
        (new_module, name),
    )
    if cr.fetchone():
        # El módulo nuevo ya reclamó su propio xmlid — nada que hacer,
        # el viejo puede quedar de lado (huérfano pero inactivo).
        return
    cr.execute(
        "SELECT id, res_id, model FROM ir_model_data WHERE module = %s AND name = %s",
        (old_module, name),
    )
    old = cr.fetchone()
    if not old:
        return
    old_id, res_id, model = old
    cr.execute(
        "UPDATE ir_model_data SET module = %s WHERE id = %s",
        (new_module, old_id),
    )
    _logger.info(
        "hooks_core_jump: xmlid %s.%s adoptado por %s (modelo %s, res_id %s)",
        old_module,
        name,
        new_module,
        model,
        res_id,
    )


def _reload_core_data_files(env):
    """Carga el XML/CSV actual de los núcleos (vistas nuevas como location.map).

    En gc 19.0.1.5.5 no existía ``view_kt_marketplace_location_map_list``
    (llegó con Falabella/Rappi). Sin ``-u``, Instalar pos_bridge/DiDi
    aborta al heredarla. Recargar el data del manifiesto la crea.
    Cada archivo va en try: un fallo (leftover combinado) no impide
    el resto.
    """
    from odoo.modules.module import get_manifest
    from odoo.tools.convert import convert_file

    installed = set(
        env["ir.module.module"]
        .sudo()
        .search([("name", "in", _CORE_MODULES), ("state", "=", "installed")])
        .mapped("name")
    )
    for module in _CORE_MODULES:
        # No alcanza con que la carpeta exista en el `addons_path`
        # (`get_module_path`) — hace falta que el módulo esté
        # REALMENTE instalado en ESTA base. Sin este chequeo, un
        # caller de este hook compartido que no dependa (ni siquiera
        # indirectamente) de `kt_marketplace_order_import`/`_feed_sync`
        # intenta recargar el data de un módulo cuyos modelos no
        # existen en el registry — `ir_model_access.csv` etc. fallan
        # con `NotNullViolation` en `model_id` (detectado 15/08/2026 al
        # correr los tests de `kt_marketplace_core_utils` en solitario,
        # sin ningún adaptador instalado — ver CHECKLIST_MODULOS_
        # ODOO.md §37). Hoy TODOS los callers reales dependen de estos
        # 2 módulos, así que nunca pasa en producción — pero vale la
        # pena que el hook compartido no asuma esa garantía por diseño.
        if module not in installed or not get_module_path(module):
            continue
        try:
            info = get_manifest(module)
        except Exception:
            _logger.warning(
                "hooks_core_jump: cannot read manifest of %s",
                module,
                exc_info=True,
            )
            continue
        for filename in info.get("data") or []:
            try:
                convert_file(env, module, filename, {}, mode="update")
            except Exception:
                _logger.warning(
                    "hooks_core_jump: could not reload %s/%s",
                    module,
                    filename,
                    exc_info=True,
                )


def _auto_init_marketplace_models(env):
    """Fuerza la creación/actualización de tabla de los modelos
    ``kt.marketplace.*`` sin esperar el próximo ``-u`` real.

    18/08/2026 (CHECKLIST_MODULOS_ODOO.md §51): llamar a
    ``model._auto_init()`` directo, fuera de una llamada activa a
    ``Registry.init_models()``, revienta con ``AttributeError:
    'Registry' object has no attribute '_post_init_queue'`` en
    cualquier modelo con un `Many2one`/`Many2many` — ese atributo es
    TRANSITORIO, Odoo lo crea y lo borra dentro de ``init_models()``
    (``odoo/orm/registry.py``), y varios ``Field._auto_init()`` del
    núcleo llaman a ``pool.post_init(...)`` esperando que exista. El
    ``try/except`` de abajo lo capturaba en silencio (como warning),
    pero eso deja el `_auto_init` real SIN EJECUTAR para todo modelo
    con una relación — hace lo mismo que el propio ``Registry.
    init_models()`` (crea/borra ``_post_init_queue`` etc. antes/después
    de cada `_auto_init()`), así que ya no puede reventar por esto.
    """
    for model_name in list(env.registry):
        if not model_name.startswith("kt.marketplace."):
            continue
        try:
            env.registry.init_models(env.cr, [model_name], {})
        except Exception:
            _logger.warning(
                "hooks_core_jump: _auto_init skipped for %s",
                model_name,
                exc_info=True,
            )


def _reapply_console_menu_reparenting(env):
    """Auto-sanación (15/08/2026, CHECKLIST_MODULOS_ODOO.md §37): bug
    real encontrado al correr el CI con `MODULES_VERIFIED` instalado
    completo (como realmente lo hace `.github/workflows/ci.yml`, no
    módulo por módulo) — `_reload_core_data_files()` de arriba
    RECARGA el XML de `kt_marketplace_order_import` (`convert_file`,
    `mode='update'`), que reescribe `parent_id`/`sequence` de sus
    menús al valor declarado en el XML (genérico) — DESHACIENDO en
    silencio el reparenting que `kt_marketplace_console.hooks.
    reparent_console_menus()` ya había aplicado al instalarse. Esto
    pasa cada vez que se instala/actualiza CUALQUIER módulo que use
    este hook compartido (cualquier adaptador de canal) DESPUÉS de
    que `kt_marketplace_console` ya esté instalado — exactamente el
    escenario que `detect_misplaced_console_menus()` (wizard de
    Mantenimiento) ya detectaba, pero solo como aviso manual, no como
    fix automático. Import perezoso y sin dependencia dura a
    propósito — `kt_marketplace_core_utils` no depende de `console`
    (es al revés), así que esto debe seguir siendo no-op si console
    no está instalado, o si el propio paquete no está en el
    ``addons_path`` de este despliegue."""
    try:
        from odoo.addons.kt_marketplace_console.hooks import reparent_console_menus
    except ImportError:
        return
    try:
        reparent_console_menus(env)
    except Exception:
        _logger.warning(
            "hooks_core_jump: no se pudo re-aplicar el reparenting de "
            "kt_marketplace_console",
            exc_info=True,
        )
