# -*- coding: utf-8 -*-
"""Ver CHECKLIST_MODULOS_ODOO.md, sección 6: escrito con cuidado,
todavía no ejecutado contra un Odoo real."""

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestKtPublicQrToken(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.template"].create(
            {
                "name": "Producto KT-Public-QR (test)",
            }
        )

    def test_regenerate_token_changes_value_and_url(self):
        old_token = self.product.kt_public_access_token
        old_url = self.product.kt_public_qr_url
        self.assertTrue(old_token)

        result = self.product.action_kt_regenerate_public_token()

        self.assertNotEqual(self.product.kt_public_access_token, old_token)
        self.assertNotEqual(self.product.kt_public_qr_url, old_url)
        self.assertIn(
            self.product.kt_public_access_token, self.product.kt_public_qr_url
        )
        self.assertEqual(result.get("type"), "ir.actions.client")
        self.assertEqual(result.get("tag"), "display_notification")

    def test_regenerate_token_multiple_products(self):
        other = self.env["product.template"].create(
            {
                "name": "Otro producto KT-Public-QR (test)",
            }
        )
        products = self.product | other
        old_tokens = {p.id: p.kt_public_access_token for p in products}

        products.action_kt_regenerate_public_token()

        for product in products:
            self.assertNotEqual(product.kt_public_access_token, old_tokens[product.id])

    def test_public_page_values_are_neutral_and_variant_aware(self):
        website = self.env["website"].search([], limit=1)
        values = self.product._kt_public_qr_page_values(website)

        self.assertEqual(values["product"], self.product)
        self.assertEqual(values["single_variant"], self.product.product_variant_id)
        self.assertEqual(values["kt_public_qr_website"], website)
        self.assertNotIn("alt_codes", values)
        self.assertNotIn("alt_codes_by_variant", values)
