# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestPaymentGatewayContract(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        partner = cls.env["res.partner"].create({"name": "Payment Core Test"})
        cls.order = cls.env["sale.order"].create({"partner_id": partner.id})

    def test_neutral_registry_is_empty(self):
        self.assertEqual(self.env["sale.order"]._kt_gateway_available_gateways(), [])

    def test_unknown_gateway_is_explicit(self):
        with self.assertRaises(UserError):
            self.order._kt_gateway_create_payment_attempt("unknown", 1.0)

    def test_neutral_hooks_are_stable(self):
        self.assertEqual(self.order._kt_get_partial_refund_amount(), 0.0)
        self.assertEqual(self.order._kt_refund_fee_gateway_guess(), "other")
        self.assertFalse(self.order._kt_gateway_pending_orders_domain())
        self.assertFalse(self.order._kt_gateway_refresh_pending_status())
