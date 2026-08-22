# -*- coding: utf-8 -*-
from odoo import api, fields, models


class KtLabelSize(models.Model):
    _name = "kt.label.size"
    _description = "Tamaño de etiqueta de producto"
    _order = "name"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    label_width_mm = fields.Float(
        string="Ancho de la etiqueta (mm)",
        required=True,
        default=60,
    )
    label_height_mm = fields.Float(
        string="Alto de la etiqueta (mm)",
        required=True,
        default=50,
    )
    content_size_mm = fields.Float(
        string="Tamaño del contenido principal dentro de la etiqueta (mm)",
        required=True,
        default=30,
        help="El QR/código de barras/imagen principal — debe ser menor "
        "al ancho y al alto de la etiqueta, dejando espacio para "
        "texto arriba y/o debajo.",
    )
    page_width_mm = fields.Float(
        string="Ancho de la hoja (mm)",
        required=True,
        default=210,
        help="210mm = A4. Para una impresora térmica de rollo "
        "continuo, poner aquí el ancho real del rollo (ej. "
        "101.6mm para un rollo de 4 pulgadas).",
    )
    page_height_mm = fields.Float(
        string="Alto de la hoja (mm)",
        required=True,
        default=297,
        help="297mm = A4. Para un rollo continuo, dejar un número "
        "grande (ej. 2000mm) — cada página del PDF resultante "
        "tendrá muchas etiquetas seguidas, aprovechando el largo "
        "real disponible del rollo.",
    )
    margin_mm = fields.Float(
        string="Margen de la hoja (mm)",
        required=True,
        default=10,
    )
    columns = fields.Integer(compute="_compute_grid", string="Columnas")
    rows = fields.Integer(compute="_compute_grid", string="Filas")

    @api.depends(
        "label_width_mm",
        "label_height_mm",
        "page_width_mm",
        "page_height_mm",
        "margin_mm",
    )
    def _compute_grid(self):
        """Calcula cuántas etiquetas caben por hoja, a partir del
        tamaño de etiqueta y de hoja — así el usuario no tiene que
        calcular la cuadrícula a mano, solo describir el tamaño físico
        real de su papel/rollo y de su etiqueta.

        Genérico a propósito — no sabe ni le importa si lo que se va
        a imprimir en cada etiqueta es un código de barras, un QR, o
        cualquier otra cosa; solo resuelve el acomodo físico."""
        for size in self:
            usable_width = size.page_width_mm - (2 * size.margin_mm)
            usable_height = size.page_height_mm - (2 * size.margin_mm)
            size.columns = (
                max(1, int(usable_width // size.label_width_mm))
                if size.label_width_mm
                else 1
            )
            size.rows = (
                max(1, int(usable_height // size.label_height_mm))
                if size.label_height_mm
                else 1
            )
