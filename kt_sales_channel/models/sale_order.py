# -*- coding: utf-8 -*-
# Copyright 2026 Kuvexta
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    kt_sales_channel_id = fields.Many2one(
        "kt.sales.channel",
        string="Canal de venta",
        index=True,
        tracking=True,
        help="Origen comercial del pedido (manual o integración).",
    )
