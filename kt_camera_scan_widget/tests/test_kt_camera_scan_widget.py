# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestKtCameraScanWidget(TransactionCase):
    """Módulo mayormente frontend (OWL) — no probable con
    TransactionCase. Solo se verifican los valores por defecto de los
    3 interruptores de configuración."""

    def test_defaults(self):
        company = self.env.company
        self.assertTrue(company.kt_camera_scan_enabled)
        self.assertTrue(company.kt_camera_scan_beep_enabled)
        self.assertEqual(company.kt_camera_scan_default_facing, "environment")
