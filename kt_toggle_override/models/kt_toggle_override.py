# -*- coding: utf-8 -*-
# Copyright 2026 Kuvexta
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
"""Excepciones por bodega a los 5 interruptores de inventario de
``kt_advanced_stock_flows`` — ver `disenos_completos/kt_toggle_
override/DISENO_ARQUITECTURA_KT_TOGGLE_OVERRIDE.md` para el alcance
completo (por qué SOLO estos 5, por qué ningún otro interruptor de
los otros 3 módulos `kt_*` lo necesita).

Sin ninguna excepción registrada, el comportamiento es idéntico al de
``kt_advanced_stock_flows`` por sí solo — este módulo es puramente
aditivo (ver ``res.company._kt_resolve_toggle``).
"""

from odoo import fields, models

# Único lugar donde se declaran los 5 interruptores válidos — si
# `kt_advanced_stock_flows` agrega o quita uno, se actualiza acá (no
# es texto libre a propósito, para no poder registrar una excepción
# de un campo que no existe o que ya no aplica este mecanismo).
TOGGLE_KEY_SELECTION = [
    ("kt_restrict_lot_by_move", "Exigir lote/serie explícito al validar"),
    ("kt_auto_create_lot_on_receipt", "Auto-crear lote en recepción"),
    ("kt_filter_lot_by_location", "Filtrar lote por ubicación de origen"),
    ("kt_lot_scrap_button", "Botón de merma total"),
    ("kt_no_negative_stock", "Bloquear stock negativo"),
]


class KtToggleOverride(models.Model):
    _name = "kt.toggle.override"
    _description = "Excepción por bodega a un interruptor de kt_advanced_stock_flows"
    _rec_name = "toggle_key"

    warehouse_id = fields.Many2one(
        "stock.warehouse",
        required=True,
        ondelete="cascade",
        index=True,
        help="La bodega a la que aplica esta excepción.",
    )
    company_id = fields.Many2one(
        related="warehouse_id.company_id", store=True, readonly=True
    )
    toggle_key = fields.Selection(
        TOGGLE_KEY_SELECTION,
        required=True,
        help="Cuál de los 5 interruptores de kt_advanced_stock_flows "
        "se está forzando para esta bodega en particular.",
    )
    value = fields.Boolean(
        string="Valor forzado",
        help="El valor que aplica SOLO para esta bodega, en vez del "
        "configurado a nivel de la compañía.",
    )

    _warehouse_toggle_uniq = models.Constraint(
        "unique(warehouse_id, toggle_key)",
        "Ya existe una excepción registrada para esa bodega y esa "
        "característica — editá la existente en vez de crear otra.",
    )
