# -*- coding: utf-8 -*-
# Copyright 2026 Kuvexta
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
"""Contrato neutral entre ``sale.order`` y adaptadores de pago.

Esta capa deliberadamente no implementa operación financiera. Los adapters
pueden encadenar estos hooks con ``super()``; las capacidades avanzadas viven
en ``kt_payment_operations``.
"""

from odoo import _, api, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _kt_gateway_available_gateways(self):
        """Lista extensible ``[(code, label), ...]`` aportada por adapters."""
        return []

    def _kt_gateway_create_payment_attempt(
        self, gateway, amount, payment_method_type=None
    ):
        """Contrato de creación de cobro; Operations aporta el modelo de intento."""
        self.ensure_one()
        raise UserError(_("Pasarela «%s» no disponible o no instalada.") % gateway)

    def _kt_get_partial_refund_amount(self):
        """Hook neutral: 0.0 significa que no se informó reembolso parcial."""
        self.ensure_one()
        return 0.0

    def _kt_refund_fee_gateway_guess(self):
        """Hook neutral para identificación extensible del provider."""
        self.ensure_one()
        return "other"

    def _kt_gateway_pending_orders_domain(self):
        """Hook neutral para adapters que puedan reconsultar pagos pendientes."""
        return False

    def _kt_gateway_refresh_pending_status(self):
        """Hook neutral de refresco de estado; por defecto no hace nada."""
        self.ensure_one()
        return False

    @api.model
    def _kt_gateway_find_order_by_settlement_reference(self, gateway, reference):
        """Resolución genérica por nombre o por el patrón ``<name>-<id>``."""
        if not reference:
            return self.browse()
        order = self.search([("name", "=", reference)], limit=1)
        if order:
            return order
        base_name = reference.rsplit("-", 1)[0]
        return self.search([("name", "=", base_name)], limit=1)
