# Copyright 2026 Kuvexta
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

from pathlib import Path
from unittest.mock import patch

from odoo.modules.module import get_module_path
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestKtCameraWebsiteResolver(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website = cls.env["website"].search([], limit=1)
        cls.public_user = cls.env.ref("base.public_user")
        cls.product = cls.env["product.template"].create(
            {
                "name": "Public camera product",
                "is_published": True,
                "sale_ok": True,
            }
        )
        cls.product.product_variant_id.barcode = "KT-CAMERA-OFFICIAL-001"

    def _resolver(self):
        return self.env["kt.camera.website.resolver"].with_user(self.public_user)

    def _public_website(self):
        return self.website.with_user(self.public_user)

    def test_published_official_barcode_returns_safe_url(self):
        result = self._resolver().resolve_code(
            "KT-CAMERA-OFFICIAL-001", self._public_website()
        )
        self.assertEqual(result["status"], "found")
        self.assertTrue(result["product_url"].startswith("/"))
        self.assertFalse(result["product_url"].startswith("//"))

    def test_unpublished_product_is_not_exposed(self):
        self.product.is_published = False
        result = self._resolver().resolve_code(
            "KT-CAMERA-OFFICIAL-001", self._public_website()
        )
        self.assertEqual(result, {"status": "not_found"})

    def test_invalid_inputs_are_rejected(self):
        resolver = self._resolver()
        website = self._public_website()
        for value in (None, "", "   ", "line\nbreak", "x" * 129):
            with self.subTest(value=value):
                self.assertEqual(
                    resolver.resolve_code(value, website), {"status": "invalid"}
                )

    def test_disabled_company_is_closed(self):
        self.website.company_id.kt_camera_scan_enabled = False
        result = self._resolver().resolve_code(
            "KT-CAMERA-OFFICIAL-001", self._public_website()
        )
        self.assertEqual(result, {"status": "disabled"})

    def test_two_eligible_candidates_are_ambiguous(self):
        second = self.env["product.template"].create(
            {"name": "Second public product", "is_published": True, "sale_ok": True}
        )
        resolver = self._resolver()
        with patch.object(
            type(resolver),
            "_official_candidate_template_ids",
            autospec=True,
            return_value=[self.product.id, second.id],
        ):
            result = resolver.resolve_code("AMBIGUOUS", self._public_website())
        self.assertEqual(result, {"status": "ambiguous"})

    def test_controller_contract_does_not_reuse_legacy_surface(self):
        controller = Path(
            get_module_path("kt_camera_scan_website_base"),
            "controllers",
            "product_resolver.py",
        ).read_text(encoding="utf-8")
        self.assertIn("/kt/camera/v1/product/resolve", controller)
        for forbidden in (
            "/shop/barcode/product",
            "/website/barcode/product",
            "last_code",
            "request.session",
            "ir.actions.act_url",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, controller)
