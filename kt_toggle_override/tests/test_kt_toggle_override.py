# -*- coding: utf-8 -*-
# Copyright 2026 Kuvexta
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
from odoo.tests.common import TransactionCase, tagged
from psycopg2 import IntegrityError


@tagged("post_install", "-at_install")
class TestKtToggleOverride(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.company.id)], limit=1
        )
        cls.other_warehouse = cls.env["stock.warehouse"].create(
            {
                "name": "Bodega Kuvexta Test",
                "code": "KTT",
                "company_id": cls.company.id,
            }
        )

    def test_no_override_falls_back_to_company_value(self):
        """Sin `kt_advanced_stock_flows` instalado (no es dependencia
        de este módulo), la compañía no tiene el atributo — el
        fallback `getattr(..., False)` debe devolver False, nunca
        romper."""
        self.assertFalse(
            self.company._kt_resolve_toggle(
                "kt_no_negative_stock", warehouse=self.warehouse
            )
        )

    def test_no_warehouse_falls_back_to_company_value(self):
        self.assertFalse(
            self.company._kt_resolve_toggle("kt_no_negative_stock", warehouse=None)
        )

    def test_override_wins_over_company_value(self):
        self.env["kt.toggle.override"].create(
            {
                "warehouse_id": self.warehouse.id,
                "toggle_key": "kt_no_negative_stock",
                "value": True,
            }
        )
        self.assertTrue(
            self.company._kt_resolve_toggle(
                "kt_no_negative_stock", warehouse=self.warehouse
            )
        )

    def test_override_only_applies_to_its_own_warehouse(self):
        self.env["kt.toggle.override"].create(
            {
                "warehouse_id": self.warehouse.id,
                "toggle_key": "kt_no_negative_stock",
                "value": True,
            }
        )
        self.assertFalse(
            self.company._kt_resolve_toggle(
                "kt_no_negative_stock", warehouse=self.other_warehouse
            )
        )

    def test_duplicate_warehouse_toggle_blocked(self):
        self.env["kt.toggle.override"].create(
            {
                "warehouse_id": self.warehouse.id,
                "toggle_key": "kt_no_negative_stock",
                "value": True,
            }
        )
        with self.assertRaises(IntegrityError):
            self.env["kt.toggle.override"].create(
                {
                    "warehouse_id": self.warehouse.id,
                    "toggle_key": "kt_no_negative_stock",
                    "value": False,
                }
            )
            self.env.flush_all()

    def test_different_toggle_key_same_warehouse_allowed(self):
        self.env["kt.toggle.override"].create(
            {
                "warehouse_id": self.warehouse.id,
                "toggle_key": "kt_no_negative_stock",
                "value": True,
            }
        )
        second = self.env["kt.toggle.override"].create(
            {
                "warehouse_id": self.warehouse.id,
                "toggle_key": "kt_lot_scrap_button",
                "value": True,
            }
        )
        self.assertTrue(second)

    def test_ir_rule_hides_other_company_override(self):
        """`company_id` (related de `warehouse_id.company_id`) debe estar
        protegido por `ir.rule` — un usuario sin acceso a la otra
        compañía no debe poder ver/buscar la excepción de esa bodega,
        aunque conozca su ID."""
        other_company = self.env["res.company"].create({"name": "KT Toggle Co B"})
        other_warehouse = self.env["stock.warehouse"].create(
            {
                "name": "Bodega Co B",
                "code": "KTB",
                "company_id": other_company.id,
            }
        )
        other_override = self.env["kt.toggle.override"].create(
            {
                "warehouse_id": other_warehouse.id,
                "toggle_key": "kt_no_negative_stock",
                "value": True,
            }
        )
        # `res.users.groups_id` -> `group_ids` en Odoo 19 (CHECKLIST_
        # MODULOS_ODOO.md §36) — se detecta el nombre real en vez de
        # asumirlo.
        group_field = (
            "group_ids" if "group_ids" in self.env["res.users"]._fields else "groups_id"
        )
        restricted_user = self.env["res.users"].create(
            {
                "name": "Usuario Solo Co A",
                "login": "kt_toggle_only_co_a",
                "company_id": self.company.id,
                "company_ids": [(6, 0, [self.company.id])],
                # `stock.group_stock_user` (no solo `base.group_user`):
                # sin esto, `search()` levanta AccessError antes de
                # llegar al ir.rule (CHECKLIST_MODULOS_ODOO.md §36).
                group_field: [
                    (
                        6,
                        0,
                        [
                            self.env.ref("base.group_user").id,
                            self.env.ref("stock.group_stock_user").id,
                        ],
                    )
                ],
            }
        )
        found = (
            self.env["kt.toggle.override"]
            .with_user(restricted_user)
            .search([("id", "=", other_override.id)])
        )
        self.assertFalse(
            found, "El usuario sin acceso a Co B no debería ver su excepción."
        )
