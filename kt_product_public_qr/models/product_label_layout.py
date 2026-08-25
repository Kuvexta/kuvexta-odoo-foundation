# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ProductLabelLayout(models.TransientModel):
    _inherit = "product.label.layout"

    print_format = fields.Selection(
        selection_add=[
            ("kt_public_qr_square", "QR público - Cuadrado (recomendado)"),
            ("kt_public_qr_custom", "QR público - Tamaño personalizado"),
            ("kt_public_qr_2x7", "QR público (2 x 7) — heredado, formato lineal"),
            ("kt_public_qr_4x7", "QR público (4 x 7) — heredado, formato lineal"),
            ("kt_public_qr_4x12", "QR público (4 x 12) — heredado, formato lineal"),
        ],
        ondelete={
            "kt_public_qr_square": "set default",
            "kt_public_qr_custom": "set default",
            "kt_public_qr_2x7": "set default",
            "kt_public_qr_4x7": "set default",
            "kt_public_qr_4x12": "set default",
        },
    )
    kt_label_size_id = fields.Many2one(
        "kt.label.size",
        string="Tamaño de etiqueta",
        help='Solo aplica con el formato "QR público - Tamaño '
        'personalizado" — administra los tamaños disponibles '
        "desde Inventario → Control de inventario → Tamaños de "
        "etiqueta (compartido con cualquier otro módulo que "
        "también imprima etiquetas, ver kt_label_printing).",
    )

    @api.depends("print_format", "kt_label_size_id")
    def _compute_dimensions(self):
        """Extiende el cómputo nativo de columnas/filas (ver
        `addons/product/wizard/product_label_layout.py`, verificado
        contra el código fuente real) — ese método parte
        `print_format` por el caracter 'x' asumiendo que TODO el
        valor es "NxM" (ej. '4x12'). Nuestros formatos nuevos tienen
        un prefijo (`kt_public_qr_2x7`) que rompería ese cálculo si
        se dejara pasar tal cual (`'kt_public_qr_2'.isdigit()` es
        `False`, cayendo al valor por defecto de 1x1). Por eso se
        intercepta aquí ANTES de llamar al método nativo, solo para
        los formatos propios.

        `kt_public_qr_square` (04/08/2026, recomendado por defecto):
        3 columnas x 5 filas — celda de ~63mm x 55mm en una hoja A4,
        genuinamente cuadrada y generosa para un QR (a diferencia de
        los formatos 2x7/4x7/4x12, heredados de las etiquetas
        nativas de código de barras LINEAL — ancho y bajo, nunca
        pensadas para un QR, que necesita ser cuadrado y de un
        tamaño mínimo razonable para poder escanearse bien)."""
        own_formats = self.filtered(
            lambda w: w.print_format and w.print_format.startswith("kt_public_qr_")
        )
        for wizard in own_formats:
            if wizard.print_format == "kt_public_qr_square":
                wizard.columns, wizard.rows = 3, 5
                continue
            if wizard.print_format == "kt_public_qr_custom":
                if wizard.kt_label_size_id:
                    wizard.columns = wizard.kt_label_size_id.columns
                    wizard.rows = wizard.kt_label_size_id.rows
                else:
                    wizard.columns, wizard.rows = 1, 1
                continue
            columns, rows = wizard.print_format.replace("kt_public_qr_", "").split("x")[
                :2
            ]
            wizard.columns = int(columns)
            wizard.rows = int(rows)
        super(ProductLabelLayout, self - own_formats)._compute_dimensions()

    def _prepare_report_data(self):
        """Extiende la preparación de datos nativa — si el formato
        elegido es uno de los nuestros, apunta al reporte propio en
        vez del nativo. El resto de la lógica (validar cantidad,
        resolver `product_tmpl_ids`/`product_ids`) se reutiliza tal
        cual del método nativo, llamándolo primero."""
        if self.print_format and self.print_format.startswith("kt_public_qr_"):
            if self.custom_quantity <= 0:
                raise UserError(_("You need to set a positive quantity."))
            if self.print_format == "kt_public_qr_custom" and not self.kt_label_size_id:
                raise UserError(
                    _(
                        "Selecciona un tamaño de etiqueta para el formato "
                        "personalizado."
                    )
                )
            if self.product_tmpl_ids:
                products = self.product_tmpl_ids.ids
                active_model = "product.template"
            elif self.product_ids:
                products = self.product_ids.mapped("product_tmpl_id").ids
                active_model = "product.template"
            else:
                raise UserError(
                    _(
                        "No product to print, if the product is archived "
                        "please unarchive it before printing its label."
                    )
                )
            xml_id = (
                "kt_product_public_qr.report_product_public_qr_"
                + self.print_format.replace("kt_public_qr_", "")
            )
            data = {
                "active_model": active_model,
                "product_tmpl_ids": products,
                "layout_wizard": self.id,
                "kt_label_size_id": self.kt_label_size_id.id,
            }
            return xml_id, data
        return super()._prepare_report_data()
