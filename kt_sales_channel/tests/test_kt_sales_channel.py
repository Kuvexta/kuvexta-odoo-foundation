# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestKtSalesChannel(TransactionCase):

    def test_seed_channels_loaded(self):
        Channel = self.env["kt.sales.channel"]
        codes = Channel.search([]).mapped("code")
        for code in (
            "local",
            "ecommerce",
            "phone",
            "email",
            "whatsapp",
            "mercadolibre",
            "falabella",
            "exito",
            "facebook",
            "tiktok",
            "homecenter",
            "rappi",
        ):
            self.assertIn(code, codes)

    def test_seed_channel_types(self):
        """API seller → integrated; tráfico/etiquetas → manual."""
        Channel = self.env["kt.sales.channel"]
        for code in ("mercadolibre", "falabella", "exito", "rappi"):
            self.assertEqual(
                Channel.search([("code", "=", code)], limit=1).channel_type,
                "integrated",
                code,
            )
        for code in (
            "local",
            "ecommerce",
            "phone",
            "email",
            "whatsapp",
            "facebook",
            "tiktok",
            "homecenter",
        ):
            self.assertEqual(
                Channel.search([("code", "=", code)], limit=1).channel_type,
                "manual",
                code,
            )

    def test_seed_channel_business_vertical(self):
        """Doc 13: retail para la mayoría, food_delivery para Rappi
        Restaurantes (código técnico sigue siendo "rappi", solo el
        nombre se aclaró)."""
        Channel = self.env["kt.sales.channel"]
        for code in (
            "mercadolibre",
            "falabella",
            "exito",
            "facebook",
            "tiktok",
            "homecenter",
        ):
            self.assertEqual(
                Channel.search([("code", "=", code)], limit=1).business_vertical,
                "retail",
                code,
            )
        rappi = Channel.search([("code", "=", "rappi")], limit=1)
        self.assertEqual(rappi.business_vertical, "food_delivery")
        self.assertEqual(rappi.name, "Rappi Restaurantes")

    def test_business_vertical_default_is_retail(self):
        channel = self.env["kt.sales.channel"].create(
            {"name": "Canal de prueba KT", "code": "kt_test_channel_vertical"}
        )
        self.assertEqual(channel.business_vertical, "retail")

    def test_sale_order_channel_selectable(self):
        partner = self.env["res.partner"].create({"name": "Cliente canal KT"})
        channel = self.env.ref("kt_sales_channel.kt_channel_whatsapp")
        order = self.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "kt_sales_channel_id": channel.id,
            }
        )
        self.assertEqual(order.kt_sales_channel_id.code, "whatsapp")

    def test_responsible_user_filters_my_channels(self):
        """Doc 11 §7.4: filtro «Mis canales» — solo devuelve los
        canales cuyo responsable es el usuario actual."""
        Channel = self.env["kt.sales.channel"]
        channel = Channel.search([("code", "=", "whatsapp")], limit=1)
        channel.responsible_user_id = self.env.uid
        my_channels = Channel.search([("responsible_user_id", "=", self.env.uid)])
        self.assertIn(channel, my_channels)

    def test_responsible_user_id_optional(self):
        channel = self.env.ref("kt_sales_channel.kt_channel_local")
        self.assertFalse(channel.responsible_user_id)

    def test_image_128_optional_and_writable(self):
        # Doc 11 §7.5: logo por canal, opcional.
        channel = self.env.ref("kt_sales_channel.kt_channel_whatsapp")
        self.assertFalse(channel.image_128)
        one_px_png = (
            b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk"
            b"+A8AAQUAB/DVzY0AAAAASUVORK5CYII="
        )
        channel.image_128 = one_px_png
        self.assertTrue(channel.image_128)

    def test_pos_config_load_fields_keeps_all_fields_sentinel(self):
        """[] = leer todos los campos (mixin POS). No truncar a un solo field."""
        pos_config = self.env["pos.config"].search([], limit=1)
        if not pos_config:
            self.skipTest("No hay pos.config disponible")
        fields_list = self.env["pos.config"]._load_pos_data_fields(pos_config)
        self.assertEqual(
            fields_list,
            [],
            "pos.config debe devolver [] para no romper load_data / currency_id",
        )

    def test_pos_config_load_read_includes_currency(self):
        pos_config = self.env["pos.config"].search([], limit=1)
        if not pos_config:
            self.skipTest("No hay pos.config disponible")
        rows = self.env["pos.config"]._load_pos_data_read(pos_config, pos_config)
        self.assertTrue(rows)
        self.assertIn("currency_id", rows[0])
        self.assertIn("use_pricelist", rows[0])
        self.assertIn("kt_sales_channel_id", rows[0])

    def test_pos_order_defaults_from_config(self):
        local = self.env.ref("kt_sales_channel.kt_channel_local")
        pos_config = self.env["pos.config"].search([], limit=1)
        if not pos_config:
            self.skipTest("No hay pos.config disponible")
        pos_config.kt_sales_channel_id = local
        session = self.env["pos.session"].search(
            [("config_id", "=", pos_config.id), ("state", "=", "opened")],
            limit=1,
        )
        if not session:
            self.skipTest("No hay sesión POS abierta para crear pedido")
        order = self.env["pos.order"].create(
            {
                "session_id": session.id,
                "amount_total": 0.0,
                "amount_tax": 0.0,
                "amount_paid": 0.0,
                "amount_return": 0.0,
            }
        )
        self.assertEqual(order.kt_sales_channel_id, local)

    def test_ir_rule_global_channel_visible_everywhere(self):
        """`company_id` vacío = "todas las compañías" (ver help del
        campo) — la `ir.rule` debe seguir mostrando los canales
        globales (los de seed, ej. `whatsapp`) a un usuario sin acceso
        a la compañía activa."""
        other_company = self.env["res.company"].create({"name": "KT Channel Co B"})
        # `res.users.groups_id` -> `group_ids` en Odoo 19 (CHECKLIST_
        # MODULOS_ODOO.md §36) — se detecta el nombre real en vez de
        # asumirlo.
        group_field = (
            "group_ids" if "group_ids" in self.env["res.users"]._fields else "groups_id"
        )
        restricted_user = self.env["res.users"].create(
            {
                "name": "Usuario Solo Co B",
                "login": "kt_channel_only_co_b",
                "company_id": other_company.id,
                "company_ids": [(6, 0, [other_company.id])],
                # `sales_team.group_sale_salesman` (no solo `base.
                # group_user`): sin esto, `search()` levanta
                # AccessError antes de llegar al ir.rule (CHECKLIST_
                # MODULOS_ODOO.md §36).
                group_field: [
                    (
                        6,
                        0,
                        [
                            self.env.ref("base.group_user").id,
                            self.env.ref("sales_team.group_sale_salesman").id,
                        ],
                    )
                ],
            }
        )
        whatsapp = self.env.ref("kt_sales_channel.kt_channel_whatsapp")
        self.assertFalse(whatsapp.company_id)
        found = (
            self.env["kt.sales.channel"]
            .with_user(restricted_user)
            .search([("id", "=", whatsapp.id)])
        )
        self.assertTrue(found, "Un canal global debe verse desde cualquier compañía.")

    def test_ir_rule_hides_other_company_channel(self):
        """Un canal atado explícitamente a UNA compañía sí debe
        aislarse — no debe verse desde otra compañía."""
        other_company = self.env["res.company"].create({"name": "KT Channel Co C"})
        own_company_channel = self.env["kt.sales.channel"].create(
            {
                "name": "Canal solo de esta compañía",
                "code": "kt_test_channel_own_company",
                "company_id": self.env.company.id,
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
                "name": "Usuario Solo Co C",
                "login": "kt_channel_only_co_c",
                "company_id": other_company.id,
                "company_ids": [(6, 0, [other_company.id])],
                # `sales_team.group_sale_salesman` (no solo `base.
                # group_user`): sin esto, `search()` levanta
                # AccessError antes de llegar al ir.rule (CHECKLIST_
                # MODULOS_ODOO.md §36).
                group_field: [
                    (
                        6,
                        0,
                        [
                            self.env.ref("base.group_user").id,
                            self.env.ref("sales_team.group_sale_salesman").id,
                        ],
                    )
                ],
            }
        )
        found = (
            self.env["kt.sales.channel"]
            .with_user(restricted_user)
            .search([("id", "=", own_company_channel.id)])
        )
        self.assertFalse(
            found,
            "Un canal atado a otra compañía no debería verse desde Co C.",
        )
