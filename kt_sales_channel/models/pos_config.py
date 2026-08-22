# -*- coding: utf-8 -*-
# Copyright 2026 Kuvexta
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
from odoo import fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    kt_sales_channel_id = fields.Many2one(
        "kt.sales.channel",
        string="Canal de venta por defecto",
        help="Se asigna a los pedidos POS de este punto de venta si no "
        "traen otro canal. Típicamente: Local (POS).",
    )

    # No override de _load_pos_data_fields: en Odoo 19 el mixin devuelve []
    # (= leer TODOS los campos). Si se hace append(['kt_sales_channel_id']),
    # el POS solo recibe ese campo, falla al leer use_pricelist/currency_id
    # y el frontend revienta con:
    # TypeError: Cannot read properties of undefined (reading 'currency_id')
    # El canal se asigna en pos.order.create (servidor); no hace falta
    # precargarlo en el JS del POS.
