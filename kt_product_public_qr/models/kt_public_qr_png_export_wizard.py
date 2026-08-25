# -*- coding: utf-8 -*-
from odoo import _, fields, models
from odoo.exceptions import UserError


class KtPublicQrPngExportWizard(models.TransientModel):
    _name = "kt.public.qr.png.export.wizard"
    _inherit = ["kt.label.png.export.mixin"]
    _description = "Exportar QR públicos como PNG (masivo)"

    product_tmpl_ids = fields.Many2many(
        "product.template",
        string="Productos",
        required=True,
    )

    def action_generate_zip(self):
        """Genera un PNG de 300x300 por cada producto seleccionado
        (llamando directo al método interno de Odoo que genera el QR,
        sin pasar por HTTP — verificado contra el código fuente real,
        `ir.actions.report.barcode()` retorna los bytes del PNG
        directamente, `barcode.asString('png')`) — la parte de
        empaquetarlos en un ZIP y armar la descarga ya no vive aquí,
        se resuelve con el mixin compartido `kt.label.png.export.mixin`
        (`kt_label_printing`), reutilizable por cualquier otro módulo
        que también necesite exportar imágenes en lote (ver
        `disenos_completos/kt_label_printing/DISENO_ARQUITECTURA_ETIQUETAS.md`)."""
        self.ensure_one()
        if not self.product_tmpl_ids:
            raise UserError(_("Selecciona al menos un producto."))

        Report = self.env["ir.actions.report"]
        files = []
        for product in self.product_tmpl_ids:
            if not product.kt_public_qr_url:
                continue
            png_bytes = Report.barcode(
                "QR",
                product.kt_public_qr_url,
                width=300,
                height=300,
            )
            files.append((product.name, png_bytes))

        return self._kt_build_zip_download_action(files, zip_filename="qr_publicos.zip")
