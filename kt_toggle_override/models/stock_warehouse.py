# -*- coding: utf-8 -*-
# Copyright 2026 Kuvexta
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    kt_toggle_override_ids = fields.One2many(
        "kt.toggle.override",
        "warehouse_id",
        string="Excepciones Kuvexta",
        help="Valores forzados para esta bodega, distintos del "
        "configurado a nivel de compañía en Inventario → Ajustes → "
        "«Kuvexta: flujos avanzados» (kt_advanced_stock_flows).",
    )
