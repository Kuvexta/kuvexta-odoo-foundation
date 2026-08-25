# Copyright 2026 Kuvexta
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

from odoo import api, models
from odoo.fields import Domain


class KtCameraWebsiteResolver(models.AbstractModel):
    _name = "kt.camera.website.resolver"
    _description = "Public website product resolver for camera scans"

    _MAX_CODE_LENGTH = 128

    @api.model
    def _normalize_code(self, code):
        if not isinstance(code, str):
            return False
        normalized = code.strip()
        if not normalized or len(normalized) > self._MAX_CODE_LENGTH:
            return False
        if any(ord(character) < 32 for character in normalized):
            return False
        return normalized

    @api.model
    def _official_candidate_template_ids(self, code, website):
        """Find official barcodes without invoking product.product search hooks."""
        templates = (
            self.env["product.template"]
            .sudo()
            .with_context(website_id=website.id)
            .search([("product_variant_ids.barcode", "=", code)])
        )
        return templates.ids

    @api.model
    def _additional_candidate_template_ids(self, code, website):
        """Extension hook for explicit bridges; Foundation adds no candidates."""
        return []

    @api.model
    def _candidate_template_ids(self, code, website):
        return sorted(
            set(self._official_candidate_template_ids(code, website))
            | set(self._additional_candidate_template_ids(code, website))
        )

    @api.model
    def _eligible_templates(self, candidate_ids, website):
        if not candidate_ids:
            return self.env["product.template"]

        # Build the website domain with the request/public user before sudo.
        # Sudo is used only to read candidates; it never removes this domain.
        public_sale_domain = website.sale_product_domain()
        domain = Domain.AND([public_sale_domain, Domain("id", "in", candidate_ids)])
        return (
            self.env["product.template"]
            .sudo()
            .with_context(website_id=website.id)
            .search(domain, order="id", limit=2)
        )

    @api.model
    def _safe_product_url(self, template, website):
        url = template.with_context(website_id=website.id)._get_product_url()
        if not isinstance(url, str) or not url.startswith("/") or url.startswith("//"):
            return False
        return url

    @api.model
    def resolve_code(self, code, website):
        website.ensure_one()
        normalized = self._normalize_code(code)
        if not normalized:
            return {"status": "invalid"}

        company = website.company_id
        if company and not company.kt_camera_scan_enabled:
            return {"status": "disabled"}

        candidate_ids = self._candidate_template_ids(normalized, website)
        templates = self._eligible_templates(candidate_ids, website)
        if not templates:
            return {"status": "not_found"}
        if len(templates) > 1:
            return {"status": "ambiguous"}

        product_url = self._safe_product_url(templates, website)
        if not product_url:
            return {"status": "not_found"}
        return {"status": "found", "product_url": product_url}
