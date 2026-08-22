# -*- coding: utf-8 -*-
# Copyright 2026 Kuvexta
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
from odoo import fields, models


class KtSalesChannel(models.Model):
    _name = "kt.sales.channel"
    _description = "Canal de venta"
    _order = "sequence, name"

    name = fields.Char(required=True, translate=True)
    code = fields.Char(
        required=True,
        index=True,
        help="Código técnico estable (ej. mercadolibre, falabella). "
        "Lo usan los adaptadores de marketplace.",
    )
    channel_type = fields.Selection(
        [
            ("manual", "Manual (sin integración)"),
            ("integrated", "Integrado (marketplace / API)"),
        ],
        required=True,
        default="manual",
    )
    business_vertical = fields.Selection(
        [
            ("retail", "Retail / e-commerce"),
            ("food_delivery", "Restaurantes / domicilios"),
            ("both", "Ambos"),
        ],
        required=True,
        default="retail",
        help="Doc `kt_marketplace_cross_cutting/13_NUCLEO_RETAIL_VS_RESTAURANTES.md` "
        "— determina qué secciones/campos son relevantes para este canal "
        "en los modelos genéricos y en Ajustes: un canal de comida no "
        "necesita bodega/guía de transporte; uno de retail no necesita "
        "grupos de modificadores ni tiempo de preparación. Es una "
        "propiedad del CANAL, no de la compañía — una misma compañía "
        "puede tener canales de ambas verticales a la vez.",
    )
    sequence = fields.Integer(default=10)
    image_128 = fields.Image(
        string="Logo",
        max_width=128,
        max_height=128,
        help="Doc 11 §7.5: logo del marketplace/canal — un logo se "
        "reconoce más rápido que leer el nombre en una celda, sobre "
        "todo con varios canales mezclados en una misma lista.",
    )
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company",
        string="Compañía",
        help="Vacío = disponible en todas las compañías.",
    )
    responsible_user_id = fields.Many2one(
        "res.users",
        string="Responsable del canal",
        help="Doc 11 §7.4: quién atiende este canal el día a día — "
        "si el negocio reparte la operación (una persona atiende "
        "Mercado Libre, otra Falabella), este campo permite filtrar "
        "«Mis canales» y es el punto de partida para asignar "
        "actividades por canal en los módulos que lo necesiten "
        "(ej. `kt_marketplace_order_import.kt_ml_question_responsible_user_id`, "
        "hoy configurado aparte porque las preguntas/claims todavía "
        "no tienen `channel_id` propio — ver doc 11 §2).",
    )
    sale_order_count = fields.Integer(compute="_compute_sale_order_count")

    _kt_sales_channel_code_uniq = models.Constraint(
        "unique(code)",
        "El código del canal de venta debe ser único.",
    )

    def _compute_sale_order_count(self):
        data = self.env["sale.order"]._read_group(
            [("kt_sales_channel_id", "in", self.ids)],
            ["kt_sales_channel_id"],
            ["__count"],
        )
        mapped = {channel.id: count for channel, count in data if channel}
        for channel in self:
            channel.sale_order_count = mapped.get(channel.id, 0)

    def action_view_sale_orders(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": self.env._("Pedidos — %s") % self.name,
            "res_model": "sale.order",
            "view_mode": "list,form",
            "domain": [("kt_sales_channel_id", "=", self.id)],
        }
