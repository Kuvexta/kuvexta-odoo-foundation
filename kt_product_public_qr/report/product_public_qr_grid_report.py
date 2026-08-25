# -*- coding: utf-8 -*-
from odoo import models
from odoo.addons.kt_label_printing.models.kt_label_grid_utils import (
    build_label_list,
    compute_page_numbers,
)


def _prepare_kt_public_qr_grid_data(env, docids, data):
    """Prepara los datos para cualquiera de los formatos de cuadrícula
    — usa las funciones GENÉRICAS de `kt_label_printing`
    (`build_label_list`, `compute_page_numbers`) para la parte que no
    tiene nada de específico a QR, en vez de reimplementarla aquí (ver
    `disenos_completos/kt_label_printing/DISENO_ARQUITECTURA_ETIQUETAS.md`
    para la razón completa de este rediseño — el 04/08/2026 esta
    lógica vivía duplicada solo en este módulo).

    Si `data` trae `kt_label_size_id` (solo en el formato "Tamaño
    personalizado"), también incluye las medidas reales de la
    etiqueta — usadas por la plantilla para dibujar el QR y la celda
    con el tamaño exacto que el usuario configuró, en vez de un
    tamaño fijo escrito en la plantilla."""
    layout_wizard = env["product.label.layout"].browse(data.get("layout_wizard"))
    product_tmpl_ids = data.get("product_tmpl_ids") or docids
    products = env["product.template"].browse(product_tmpl_ids)
    copies = layout_wizard.custom_quantity or 1
    labels = build_label_list(products, copies)
    result = {
        "labels": labels,
        "columns": layout_wizard.columns,
        "rows": layout_wizard.rows,
        "page_numbers": compute_page_numbers(
            len(labels), layout_wizard.columns, layout_wizard.rows
        ),
    }
    label_size_id = data.get("kt_label_size_id")
    if label_size_id:
        # `kt.label.size` vive en kt_label_printing (compartido) — el
        # campo se llama `content_size_mm` ahí (genérico, no
        # `qr_size_mm`), ya que ese módulo no sabe ni le importa qué
        # se va a dibujar dentro.
        size = env["kt.label.size"].browse(label_size_id)
        result.update(
            {
                "kt_label_width_mm": size.label_width_mm,
                "kt_label_height_mm": size.label_height_mm,
                "kt_qr_size_mm": size.content_size_mm,
            }
        )
    return result


class ReportProductPublicQrCustom(models.AbstractModel):
    _name = "report.kt_product_public_qr.report_kt_qr_custom_document"
    _description = "Etiqueta QR pública de producto - Tamaño personalizado"

    def _get_report_values(self, docids, data):
        return _prepare_kt_public_qr_grid_data(self.env, docids, data)


class ReportProductPublicQrSquare(models.AbstractModel):
    _name = "report.kt_product_public_qr.report_kt_qr_square_document"
    _description = "Etiqueta QR pública de producto - Cuadrado"

    def _get_report_values(self, docids, data):
        return _prepare_kt_public_qr_grid_data(self.env, docids, data)


class ReportProductPublicQr2x7(models.AbstractModel):
    _name = "report.kt_product_public_qr.report_kt_qr_2x7_document"
    _description = "Etiqueta QR pública de producto - 2x7"

    def _get_report_values(self, docids, data):
        return _prepare_kt_public_qr_grid_data(self.env, docids, data)


class ReportProductPublicQr4x7(models.AbstractModel):
    _name = "report.kt_product_public_qr.report_kt_qr_4x7_document"
    _description = "Etiqueta QR pública de producto - 4x7"

    def _get_report_values(self, docids, data):
        return _prepare_kt_public_qr_grid_data(self.env, docids, data)


class ReportProductPublicQr4x12(models.AbstractModel):
    _name = "report.kt_product_public_qr.report_kt_qr_4x12_document"
    _description = "Etiqueta QR pública de producto - 4x12"

    def _get_report_values(self, docids, data):
        return _prepare_kt_public_qr_grid_data(self.env, docids, data)
