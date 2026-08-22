# -*- coding: utf-8 -*-
# Copyright 2026 Kuvexta
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
from odoo import api, fields, models


class PosOrder(models.Model):
    _inherit = "pos.order"

    kt_sales_channel_id = fields.Many2one(
        "kt.sales.channel",
        string="Canal de venta",
        index=True,
        help="Canal comercial del ticket POS.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        Channel = self.env["kt.sales.channel"]
        local_channel = Channel.search([("code", "=", "local")], limit=1)
        for vals in vals_list:
            if vals.get("kt_sales_channel_id"):
                continue
            config = False
            if vals.get("config_id"):
                config = self.env["pos.config"].browse(vals["config_id"])
            elif vals.get("session_id"):
                session = self.env["pos.session"].browse(vals["session_id"])
                config = session.config_id
            if config and config.kt_sales_channel_id:
                vals["kt_sales_channel_id"] = config.kt_sales_channel_id.id
            elif local_channel:
                vals["kt_sales_channel_id"] = local_channel.id
        return super().create(vals_list)
