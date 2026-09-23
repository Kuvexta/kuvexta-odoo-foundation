# -*- coding: utf-8 -*-
"""La rejilla PDF de etiquetas, en el asistente nativo de Imprimir etiquetas.

El asistente `product.label.layout` es por donde se imprime desde la
interfaz: su botón Imprimir llama a `process()`, que pregunta a
`_prepare_report_data()` qué informe usar según `print_format`. Por eso la
rejilla PDF entra como **una opción más de `print_format`** —«Rejilla PDF
Kuvexta»—, con su tamaño de etiqueta, igual que ya hace
`kt_product_public_qr`. Sin esa opción el informe existiría pero nadie
llegaría a él.

Con esa opción, y solo con ella, el asistente avisa **antes** de imprimir de
qué saldrá sin su código propio. La hoja lleva **solo etiquetas** — en papel
adhesivo cualquier aviso impreso ocuparía celdas y desplazaría la
cuadrícula —, así que el recuento tiene que verse aquí. Quien recibe la
mercancía necesita saber dos cosas distintas, y por eso se cuentan aparte:

- cuántos salen con el **SKU** en vez de su código de barras: la etiqueta se
  lee, pero el código impreso no es el del fabricante;
- cuántos salen **sin gráfico**: o no tienen ningún código, o el que tienen no
  se puede codificar, y eso último es un dato que alguien debería corregir.

Enterarse en el muelle, intentando escanear, es tarde.

Las **cantidades** no se calculan aquí: con la opción propia se llama igual a
la cadena nativa, y es ella —`product` y, desde una recepción, `stock`— la
que construye `quantity_by_product` y `custom_barcodes`. Esta opción solo
cambia a qué informe van y le añade el tamaño.
"""

from markupsafe import Markup
from odoo import _, api, fields, models
from odoo.addons.kt_label_printing.report.kt_label_grid_report import (
    KT_CODE_SKU,
    KT_PRINT_FORMAT,
    KT_REASON_UNENCODABLE,
    KT_REPORT_XMLID,
)
from odoo.exceptions import UserError


class ProductLabelLayout(models.TransientModel):
    _inherit = "product.label.layout"

    print_format = fields.Selection(
        selection_add=[(KT_PRINT_FORMAT, "Rejilla PDF Kuvexta")],
        ondelete={KT_PRINT_FORMAT: "set default"},
    )
    kt_label_size_id = fields.Many2one(
        "kt.label.size",
        string="Tamaño de etiqueta",
        help="La hoja y la etiqueta reales: de aquí salen columnas, filas, "
        "tamaño de celda y del código de barras de la rejilla PDF.",
    )
    kt_label_code_warning = fields.Html(
        string="Códigos de las etiquetas",
        compute="_compute_kt_label_code_warning",
        help="Qué productos de esta tanda saldrán sin su código de barras "
        "propio, y por qué.",
    )

    @api.depends("print_format", "kt_label_size_id")
    def _compute_dimensions(self):
        """Columnas y filas de la opción propia salen de `kt.label.size`.

        El cómputo nativo parte `print_format` por la 'x' suponiendo un
        valor «NxM»; con el nuestro caería a 1x1. Se resuelve aquí solo la
        opción propia y el resto pasa al nativo.
        """
        own = self.filtered(lambda w: w.print_format == KT_PRINT_FORMAT)
        for wizard in own:
            size = wizard.kt_label_size_id
            wizard.columns = size.columns if size else 1
            wizard.rows = size.rows if size else 1
        return super(ProductLabelLayout, self - own)._compute_dimensions()

    @api.depends("print_format", "product_tmpl_ids", "product_ids")
    def _compute_kt_label_code_warning(self):
        """El aviso existe solo con la rejilla PDF Kuvexta.

        Los formatos estándar imprimen su propio informe, que no aplica este
        respaldo; avisarles de él sería falso, y clasificar para nada genera
        una imagen de código de barras por producto.
        """
        report = self.env["report.kt_label_printing.report_kt_label_grid_document"]
        for wizard in self:
            if wizard.print_format != KT_PRINT_FORMAT:
                wizard.kt_label_code_warning = False
                continue
            as_sku = []
            no_graphic = []
            for product in wizard._kt_variants():
                _code, kind, reason = report._kt_printable_label_code(product)
                label = product.default_code or product.display_name
                if kind == KT_CODE_SKU:
                    as_sku.append(label)
                elif reason == KT_REASON_UNENCODABLE:
                    no_graphic.append("%s (su código no se puede imprimir)" % label)
                elif not kind:
                    no_graphic.append("%s (sin ningún código)" % label)
            wizard.kt_label_code_warning = self._kt_render_warning(as_sku, no_graphic)

    def _kt_variants(self):
        """Las variantes que se imprimirán: la etiqueta es de la variante.

        Desde variantes —una recepción, por ejemplo—, esas mismas; desde
        plantillas, sus variantes, como hace el informe.
        """
        self.ensure_one()
        if self.product_ids:
            return self.product_ids
        return self.product_tmpl_ids.product_variant_ids

    def _prepare_report_data(self):
        """Con la opción propia, el botón Imprimir va a la rejilla PDF.

        Llama **siempre** a la cadena nativa: la cantidad de cada producto
        —las copias, o con «cantidades de la operación» lo recibido por
        variante y los lotes— la construyen `product` y `stock`, y aquí se
        respeta tal cual. Solo se cambia el informe y se añade el tamaño.
        """
        if self.print_format != KT_PRINT_FORMAT:
            return super()._prepare_report_data()
        if not self.kt_label_size_id:
            raise UserError(
                _("Selecciona un tamaño de etiqueta para la rejilla PDF Kuvexta.")
            )
        _native_xml_id, data = super()._prepare_report_data()
        data["kt_label_size_id"] = self.kt_label_size_id.id
        return KT_REPORT_XMLID, data

    @staticmethod
    def _kt_render_warning(as_sku, no_graphic):
        """El texto del aviso. Estático y sin formato rebuscado a propósito:
        se lee de un vistazo antes de darle a imprimir.

        Nombres y códigos los escribe quien da de alta el producto, así que
        entran **escapados**: `Markup % valores` escapa cada valor, y un
        «Tornillo <M6> & tuerca» se lee tal cual en vez de romper el HTML.
        """
        if not as_sku and not no_graphic:
            return False
        parts = []
        if as_sku:
            parts.append(
                Markup(
                    "<p><b>%d con el SKU en vez de su código de barras</b> "
                    "(se leen, pero el código impreso no es el del fabricante): "
                    "%s</p>"
                )
                % (len(as_sku), ", ".join(as_sku))
            )
        if no_graphic:
            parts.append(
                Markup(
                    "<p><b>%d sin código de barras impreso</b> "
                    "(la etiqueta sale igual, con nombre y referencia): "
                    "%s</p>"
                )
                % (len(no_graphic), ", ".join(no_graphic))
            )
        return Markup("").join(parts)
