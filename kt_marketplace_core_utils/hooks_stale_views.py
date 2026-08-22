# -*- coding: utf-8 -*-
# Copyright 2026 Kuvexta
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
"""Purga vistas ML/Éxito huérfanas del núcleo 19.0.1.5.5.

Autocontenido (no importa otros addons custom): en ``gc`` se copian
zips de un adaptador sin actualizar ``kt_product_multi_barcode`` y un
``from odoo.addons.kt_product_multi_barcode...`` aborta el ``-i``.

Hasta el 13/08/2026 este archivo vivía copiado byte a byte idéntico
en 8 módulos adaptadores de canal — ver
``disenos_completos/kt_marketplace_cross_cutting/
16_KT_MARKETPLACE_CORE_UTILS_HOOKS_COMPARTIDOS.md`` para el porqué de
la extracción a este módulo.
"""
import logging

from odoo.tools.sql import table_exists

_logger = logging.getLogger(__name__)

_NEEDLES = (
    "kt_ml_order_import_enabled",
    "kt_ml_client_id",
    "kt_ml_access_token",
    "kt_ml_order_status",
    "kt_ml_shipment_ids",
    "kt_ml_account_id",
    "kt_ml_pack_id",
    "kt_exito_order_import_enabled",
)
_KEEP_MODULES = ("kt_marketplace_mercadolibre", "kt_marketplace_exito")


def purge_stale_extracted_core_views(env):
    """Borra leftovers y limpia caché ORM/registry. Idempotente."""
    purged = _purge_stale_extracted_core_views_cr(env.cr)
    _invalidate_view_caches(env)
    return purged


def _purge_stale_extracted_core_views_cr(cr):
    if not table_exists(cr, "ir_ui_view"):
        return 0
    clauses = " OR ".join(["v.arch_db::text ILIKE %s"] * len(_NEEDLES))
    like_params = ["%" + needle + "%" for needle in _NEEDLES]
    cr.execute(
        """
        SELECT DISTINCT v.id
          FROM ir_ui_view v
          LEFT JOIN ir_model_data d
            ON d.model = 'ir.ui.view' AND d.res_id = v.id
         WHERE (%s)
           AND (
                d.id IS NULL
                OR d.module NOT IN %%s
           )
        """
        % clauses,
        [*like_params, _KEEP_MODULES],
    )
    view_ids = [row[0] for row in cr.fetchall()]
    purged = _purge_view_ids(cr, view_ids)
    if purged:
        _logger.info(
            "stale ML/Éxito views purged: %s ids=%s",
            purged,
            view_ids,
        )
    cr.execute(
        """
        UPDATE ir_ui_view v
           SET active = FALSE
         WHERE v.active IS TRUE
           AND (%s)
           AND NOT EXISTS (
                SELECT 1 FROM ir_model_data d
                 WHERE d.model = 'ir.ui.view' AND d.res_id = v.id
                   AND d.module IN %%s
           )
        """
        % clauses,
        [*like_params, _KEEP_MODULES],
    )
    deactivated = cr.rowcount
    if deactivated:
        _logger.info("stale ML/Éxito views deactivated: %s", deactivated)
    return purged + (deactivated or 0)


def _collect_view_ids_with_descendants(cr, view_ids):
    """Incluye hijas/nietas: ``inherit_id`` es ``ondelete=restrict``."""
    ids = list(dict.fromkeys(int(view_id) for view_id in view_ids if view_id))
    if not ids:
        return []
    cr.execute(
        """
        WITH RECURSIVE tree AS (
            SELECT id FROM ir_ui_view WHERE id = ANY(%s)
            UNION
            SELECT v.id
              FROM ir_ui_view v
              JOIN tree t ON v.inherit_id = t.id
        )
        SELECT id FROM tree
        """,
        (ids,),
    )
    return [row[0] for row in cr.fetchall()]


def _purge_view_ids(cr, view_ids):
    """Borra vistas y descendientes sin violar el CHECK de Odoo 19.

    ``ir.ui.view`` declara
    ``CHECK (mode != 'extension' OR inherit_id IS NOT NULL)``.
    Un ``UPDATE inherit_id = NULL`` con ``mode = extension`` aborta
    CUALQUIER Instalar/Actualizar con *Modo de herencia no válido*.
    """
    if not view_ids:
        return 0
    view_ids = _collect_view_ids_with_descendants(cr, view_ids)
    if not view_ids:
        return 0
    # Mismo statement: el CHECK ve mode=primary e inherit_id NULL juntos.
    cr.execute(
        """
        UPDATE ir_ui_view
           SET mode = 'primary', inherit_id = NULL
         WHERE id = ANY(%s)
        """,
        (view_ids,),
    )
    if table_exists(cr, "ir_ui_view_group_rel"):
        cr.execute(
            "DELETE FROM ir_ui_view_group_rel WHERE view_id = ANY(%s)",
            (view_ids,),
        )
    if table_exists(cr, "ir_act_window_view"):
        cr.execute(
            "DELETE FROM ir_act_window_view WHERE view_id = ANY(%s)",
            (view_ids,),
        )
    cr.execute(
        "UPDATE ir_act_window SET view_id = NULL WHERE view_id = ANY(%s)",
        (view_ids,),
    )
    cr.execute("DELETE FROM ir_ui_view WHERE id = ANY(%s)", (view_ids,))
    cr.execute(
        """
        DELETE FROM ir_model_data
        WHERE model = 'ir.ui.view' AND res_id = ANY(%s)
        """,
        (view_ids,),
    )
    return len(view_ids)


def _invalidate_view_caches(env):
    invalidate = getattr(env, "invalidate_all", None)
    if invalidate:
        invalidate()
    registry = env.registry
    for name in ("clear_all_caches", "clear_cache"):
        clearer = getattr(registry, name, None)
        if not clearer:
            continue
        try:
            clearer()
            return
        except TypeError:
            try:
                clearer("default")
                return
            except Exception:
                continue
        except Exception:
            continue
