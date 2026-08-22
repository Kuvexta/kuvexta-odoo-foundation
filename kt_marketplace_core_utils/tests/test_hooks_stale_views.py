# -*- coding: utf-8 -*-
# Copyright 2026 Kuvexta
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
"""Tests genéricos de la purga de vistas huérfanas, contra ``res.partner``
(siempre disponible con solo ``base`` instalado) en vez de las vistas
reales de ``kt_marketplace_order_import`` — esos escenarios completos
(CHECK de herencia, vistas hijas, etc.) ya están cubiertos en
``kt_marketplace_order_import/tests/test_stale_extracted_views.py``.
"""
from odoo.addons.kt_marketplace_core_utils.hooks_stale_views import (
    purge_stale_extracted_core_views,
)
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestHooksStaleViews(TransactionCase):
    def _inject_leftover_view(self, needle):
        parent = self.env.ref("base.view_partner_form")
        leftover = self.env["ir.ui.view"].create(
            {
                "name": "stale.test.partner.form",
                "model": "res.partner",
                "inherit_id": parent.id,
                "arch": """
                    <xpath expr="//form" position="inside">
                        <field name="company_id" invisible="1"/>
                    </xpath>
                """,
            }
        )
        # `arch_db` es `jsonb` en builds recientes de Odoo 19
        # (traducciones) pero texto plano en builds anteriores de la
        # misma rama — se detecta el tipo real de la columna en vez de
        # asumirlo (CHECKLIST_MODULOS_ODOO.md §37).
        self.env.cr.execute(
            "SELECT data_type FROM information_schema.columns "
            "WHERE table_name = 'ir_ui_view' AND column_name = 'arch_db'"
        )
        (arch_db_type,) = self.env.cr.fetchone()
        cast_back = "::jsonb" if arch_db_type == "jsonb" else ""
        self.env.cr.execute(
            f"UPDATE ir_ui_view SET arch_db = replace(arch_db::text, "
            f"'company_id', %s){cast_back} WHERE id = %s",
            (needle, leftover.id),
        )
        self.env.invalidate_all()
        return leftover

    def test_purge_is_idempotent_without_leftovers(self):
        purge_stale_extracted_core_views(self.env)
        purge_stale_extracted_core_views(self.env)

    def test_purge_removes_orphan_leftover_view(self):
        leftover = self._inject_leftover_view("kt_ml_client_id")
        leftover_id = leftover.id
        purge_stale_extracted_core_views(self.env)
        self.assertFalse(self.env["ir.ui.view"].browse(leftover_id).exists())

    def test_purge_keeps_view_tracked_by_keep_module(self):
        leftover = self._inject_leftover_view("kt_ml_access_token")
        self.env["ir.model.data"].create(
            {
                "name": "view_stale_test_keep",
                "model": "ir.ui.view",
                "module": "kt_marketplace_mercadolibre",
                "res_id": leftover.id,
                "noupdate": True,
            }
        )
        self.env.invalidate_all()
        purge_stale_extracted_core_views(self.env)
        self.assertTrue(leftover.exists())

    def test_purge_ignores_views_without_needle(self):
        leftover = self.env["ir.ui.view"].create(
            {
                "name": "not.stale.partner.form",
                "model": "res.partner",
                "inherit_id": self.env.ref("base.view_partner_form").id,
                "arch": """
                    <xpath expr="//form" position="inside">
                        <field name="company_id" invisible="1"/>
                    </xpath>
                """,
            }
        )
        purge_stale_extracted_core_views(self.env)
        self.assertTrue(leftover.exists())
