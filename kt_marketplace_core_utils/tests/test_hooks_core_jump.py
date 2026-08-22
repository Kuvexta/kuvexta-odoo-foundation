# -*- coding: utf-8 -*-
# Copyright 2026 Kuvexta
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
"""Tests genéricos: no dependen de que ningún adaptador esté instalado.

Los tests que ejercitan el comportamiento real de la migración 1.5.5→
genérico (con fixtures propias de ``kt_marketplace_order_import``,
ej. ``model_kt_ml_question``) siguen viviendo en
``kt_marketplace_order_import/tests/test_generic_core_jump.py`` — acá
solo se prueban los helpers en sí, contra datos sintéticos.
"""
from odoo.addons.kt_marketplace_core_utils.hooks_core_jump import (
    _adopt_cross_module_xmlid,
    _alias_xmlid,
    apply_generic_core_jump,
)
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestHooksCoreJump(TransactionCase):
    def _make_xmlid(self, module, name, model="ir.cron", res_id=None):
        if res_id is None:
            res_id = self.env["ir.cron"].search([], limit=1).id
        return self.env["ir.model.data"].create(
            {
                "module": module,
                "name": name,
                "model": model,
                "res_id": res_id,
            }
        )

    def test_apply_generic_core_jump_is_idempotent_without_adapters(self):
        """Sin ningún módulo kt_marketplace_* instalado, no debe fallar."""
        apply_generic_core_jump(self.env)
        apply_generic_core_jump(self.env)

    def test_alias_xmlid_renames_when_new_missing(self):
        """``_alias_xmlid`` renombra IN PLACE (``UPDATE ... SET name``,
        mismo ``id``) cuando el xmlid nuevo todavía no existe — no
        borra y recrea. La fila (``old.id``) sigue existiendo; lo que
        cambia es su ``name`` — no hay ningún xmlid ``old_name_1``
        bajo ese módulo después del rename."""
        old = self._make_xmlid("test_core_utils", "old_name_1")
        old_id = old.id
        _alias_xmlid(self.env.cr, "test_core_utils", "old_name_1", "new_name_1")
        self.env.invalidate_all()
        stale_name = self.env["ir.model.data"].search(
            [("module", "=", "test_core_utils"), ("name", "=", "old_name_1")]
        )
        self.assertFalse(stale_name)
        renamed = self.env["ir.model.data"].search(
            [("module", "=", "test_core_utils"), ("name", "=", "new_name_1")]
        )
        self.assertTrue(renamed)
        self.assertEqual(renamed.id, old_id)

    def test_alias_xmlid_deletes_old_when_both_exist(self):
        old = self._make_xmlid("test_core_utils", "old_name_2")
        self._make_xmlid("test_core_utils", "new_name_2")
        old_id = old.id
        _alias_xmlid(self.env.cr, "test_core_utils", "old_name_2", "new_name_2")
        self.env.invalidate_all()
        self.assertFalse(self.env["ir.model.data"].browse(old_id).exists())

    def test_alias_xmlid_noop_when_old_missing(self):
        # No debe crear nada ni fallar si el xmlid viejo nunca existió.
        _alias_xmlid(self.env.cr, "test_core_utils", "never_existed", "new_name_3")
        found = self.env["ir.model.data"].search(
            [("module", "=", "test_core_utils"), ("name", "=", "new_name_3")]
        )
        self.assertFalse(found)

    def test_adopt_cross_module_xmlid_moves_when_new_module_absent(self):
        old = self._make_xmlid("kt_old_module_test", "ir_cron_shared_name")
        _adopt_cross_module_xmlid(
            self.env.cr,
            "kt_old_module_test",
            "ir_cron_shared_name",
            "kt_new_module_test",
        )
        self.env.invalidate_all()
        old.invalidate_recordset()
        self.assertEqual(old.module, "kt_new_module_test")

    def test_adopt_cross_module_xmlid_noop_when_new_module_already_claimed(self):
        old = self._make_xmlid("kt_old_module_test", "ir_cron_shared_name_2")
        self._make_xmlid("kt_new_module_test", "ir_cron_shared_name_2")
        _adopt_cross_module_xmlid(
            self.env.cr,
            "kt_old_module_test",
            "ir_cron_shared_name_2",
            "kt_new_module_test",
        )
        self.env.invalidate_all()
        old.invalidate_recordset()
        # El módulo nuevo ya tiene su propia fila: la vieja se deja
        # de lado tal cual (huérfana pero sin tocar), no se fusiona.
        self.assertEqual(old.module, "kt_old_module_test")

    def test_adopt_cross_module_xmlid_noop_when_old_missing(self):
        # No debe crear nada ni fallar si el xmlid viejo nunca existió.
        _adopt_cross_module_xmlid(
            self.env.cr,
            "kt_old_module_test",
            "never_existed_cron",
            "kt_new_module_test",
        )
        found = self.env["ir.model.data"].search(
            [("module", "=", "kt_new_module_test"), ("name", "=", "never_existed_cron")]
        )
        self.assertFalse(found)
