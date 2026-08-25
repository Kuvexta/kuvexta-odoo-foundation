# Copyright 2026 Kuvexta
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

from odoo import http
from odoo.http import request


class KtCameraWebsiteProductResolver(http.Controller):
    @http.route(
        "/kt/camera/v1/product/resolve",
        type="jsonrpc",
        auth="public",
        website=True,
        methods=["POST"],
    )
    def resolve_product_code(self, code=None):
        """Return a small, stable public result without mutating the session."""
        return request.env["kt.camera.website.resolver"].resolve_code(
            code, request.website
        )
