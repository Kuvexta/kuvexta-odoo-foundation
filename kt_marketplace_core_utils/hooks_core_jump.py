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
    ("kt_marketplace_order_import", "model_kt_ml_question", "model_kt_marketplace_question"),
    ("kt_marketplace_order_import", "model_kt_ml_claim", "model_kt_marketplace_claim"),
    ("kt_marketplace_order_import", "model_kt_ml_product_binding", "model_kt_marketplace_product_binding"),
    ("kt_marketplace_feed_sync", "model_kt_ml_category_map", "model_kt_marketplace_category_map"),
    ("kt_marketplace_order_import", "view_kt_ml_question_list", "view_kt_marketplace_question_list"),
    ("kt_marketplace_order_import", "view_kt_ml_question_form", "view_kt_marketplace_question_form"),
    ("kt_marketplace_order_import", "view_kt_ml_question_search", "view_kt_marketplace_question_search"),
    ("kt_marketplace_order_import", "view_kt_ml_product_binding_list", "view_kt_marketplace_product_binding_list"),
    ("kt_marketplace_order_import", "view_kt_ml_product_binding_form", "view_kt_marketplace_product_binding_form"),
    ("kt_marketplace_order_import", "view_kt_ml_product_binding_search", "view_kt_marketplace_product_binding_search"),
    ("kt_marketplace_order_import", "view_kt_ml_claim_list", "view_kt_marketplace_claim_list"),
    ("kt_marketplace_order_import", "view_kt_ml_claim_form", "view_kt_marketplace_claim_form"),
    ("kt_marketplace_feed_sync", "view_kt_ml_category_map_list", "view_kt_marketplace_category_map_list"),
    ("kt_marketplace_feed_sync", "view_kt_ml_category_map_form", "view_kt_marketplace_category_map_form"),
    ("kt_marketplace_order_import", "action_kt_ml_product_binding", "action_kt_marketplace_product_binding"),
    ("kt_marketplace_order_import", "menu_kt_ml_product_binding", "menu_kt_marketplace_product_binding"),
    ("kt_marketplace_order_import", "action_kt_ml_question", "action_kt_marketplace_question"),
    ("kt_marketplace_order_import", "menu_kt_ml_question", "menu_kt_marketplace_question"),
    ("kt_marketplace_order_import", "action_kt_ml_claim", "action_kt_marketplace_claim"),
    ("kt_marketplace_order_import", "menu_kt_ml_claim", "menu_kt_marketplace_claim"),
    ("kt_marketplace_feed_sync", "action_kt_ml_category_map", "action_kt_marketplace_category_map"),
    ("kt_marketplace_feed_sync", "menu_kt_ml_category_map", "menu_kt_marketplace_category_map"),
)

_CORE_MODULES = ("kt_marketplace_order_import", "kt_marketplace_feed_sync")

_CRON_MODULE_MIGRATIONS = (
    ("kt_marketplace_order_import", "ir_cron_kt_ml_poll_orders", "kt_marketplace_mercadolibre"),
    ("kt_marketplace_order_import", "ir_cron_kt_ml_refresh_tokens", "kt_marketplace_mercadolibre"),
    ("kt_marketplace_order_import", "ir_cron_kt_ml_resync_status", "kt_marketplace_mercadolibre"),
    ("kt_marketplace_order_import", "ir_cron_kt_ml_question_sla", "kt_marketplace_mercadolibre"),
    ("kt_marketplace_order_import", "ir_cron_kt_ml_feed_stock_price", "kt_marketplace_mercadolibre"),
    ("kt_marketplace_order_import", "ir_cron_kt_ml_category_attributes", "kt_marketplace_mercadolibre"),
    ("kt_marketplace_order_import", "ir_cron_kt_ml_health_check", "kt_marketplace_mercadolibre"),
    ("kt_marketplace_order_import", "ir_cron_kt_ml_ads_sync", "kt_marketplace_mercadolibre"),
)


def apply_generic_core_jump(env):
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
    clearer = getattr(env.registry, "clear_cache", None) or getattr(env.registry, "clear_all_caches", None)
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
    cr.execute("SELECT id, model, res_id FROM ir_model_data WHERE module = %s AND name = %s", (module, old_name))
    old = cr.fetchone()
    cr.execute("SELECT id FROM ir_model_data WHERE module = %s AND name = %s", (module, new_name))
    new = cr.fetchone()
    if old and not new:
        cr.execute("UPDATE ir_model_data SET name = %s WHERE id = %s", (new_name, old[0]))
        _logger.info("hooks_core_jump: xmlid %s.%s → %s", module, old_name, new_name)
        return
    if old and new:
        cr.execute("DELETE FROM ir_model_data WHERE id = %s", (old[0],))


def _adopt_cross_module_xmlid(cr, old_module, name, new_module):
    cr.execute("SELECT id FROM ir_model_data WHERE module = %s AND name = %s", (new_module, name))
    if cr.fetchone():
        return
    cr.execute("SELECT id, res_id, model FROM ir_model_data WHERE module = %s AND name = %s", (old_module, name))
    old = cr.fetchone()
    if not old:
        return
    old_id, res_id, model = old
    cr.execute("UPDATE ir_model_data SET module = %s WHERE id = %s", (new_module, old_id))
    _logger.info("hooks_core_jump: xmlid %s.%s adoptado por %s (modelo %s, res_id %s)", old_module, name, new_module, model, res_id)


def _reload_core_data_files(env):
    from odoo.modules.module import get_manifest
    from odoo.tools.convert import convert_file
    installed = set(env["ir.module.module"].sudo().search([("name", "in", _CORE_MODULES), ("state", "=", "installed")]).mapped("name"))
    for module in _CORE_MODULES:
        if module not in installed or not get_module_path(module):
            continue
        try:
            info = get_manifest(module)
        except Exception:
            _logger.warning("hooks_core_jump: cannot read manifest of %s", module, exc_info=True)
            continue
        for filename in info.get("data") or []:
            try:
                convert_file(env, module, filename, {}, mode="update")
            except Exception:
                _logger.warning("hooks_core_jump: could not reload %s/%s", module, filename, exc_info=True)


def _auto_init_marketplace_models(env):
    for model_name in list(env.registry):
        if not model_name.startswith("kt.marketplace."):
            continue
        try:
            env.registry.init_models(env.cr, [model_name], {})
        except Exception:
            _logger.warning("hooks_core_jump: _auto_init skipped for %s", model_name, exc_info=True)


def _reapply_console_menu_reparenting(env):
    try:
        from odoo.addons.kt_marketplace_console.hooks import reparent_console_menus
    except ImportError:
        return
    try:
        reparent_console_menus(env)
    except Exception:
        _logger.warning("hooks_core_jump: no se pudo re-aplicar el reparenting de kt_marketplace_console", exc_info=True)
