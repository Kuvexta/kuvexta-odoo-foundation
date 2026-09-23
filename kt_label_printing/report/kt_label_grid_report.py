# -*- coding: utf-8 -*-
"""Datos del informe de etiquetas en cuadrícula de `kt_label_printing`.

Este módulo administraba tamaños y calculaba cuadrículas, pero no dibujaba
nada: su única salida era un ZIP de PNG armado con bytes que le pasaba el
módulo consumidor. El piloto de recepción necesita un PDF, porque una hoja
con una cuadrícula de etiquetas se imprime de una vez y un ZIP obliga a abrir
e imprimir una por una — y en recepción se recibe un lote.

El PDF **reutiliza lo que ya existía** en vez de duplicarlo: la geometría
de `kt.label.size` (incluidos `columns`/`rows`, que son campos calculados),
`compute_page_numbers()`, y el asistente nativo `product.label.layout` con
**sus cantidades tal como las construyen Odoo y stock** —`quantity_by_product`
y `custom_barcodes`, incluidas las «cantidades de la operación» de una
recepción—. Lo propio es qué se dibuja en cada celda.

La etiqueta es **de la variante** (`product.product`): su `barcode` es el de
la variante. Lanzado desde plantillas, cada plantilla se imprime como sus
variantes, para no perder ese código.
"""

import base64

from odoo import _, api, models
from odoo.addons.kt_label_printing.models.kt_label_grid_utils import (
    compute_page_numbers,
)
from odoo.exceptions import UserError

#: Código tomado del campo oficial `barcode` del producto.
KT_CODE_BARCODE = "barcode"
#: Código tomado de la referencia interna (`default_code`), impreso en
#: Code128 y **marcado en la etiqueta como SKU**, para que quien la lea no lo
#: confunda con un EAN del fabricante.
KT_CODE_SKU = "sku"
#: El código elegido existía pero la simbología no lo puede codificar, así que
#: la etiqueta cae a (c). Se cuenta y se lista aparte de los que no tenían
#: ningún código: no es lo mismo «no hay código» que «hay uno y no imprime».
KT_REASON_UNENCODABLE = "unencodable"
#: **Reservado; ya no se imprime como gráfico.** Hasta 19.0.1.0.2 marcaba la
#: etiqueta cuyo gráfico era el código del lote o serie, como hace el nativo.
#: Desde 19.0.1.1.0 el gráfico es siempre el del producto y el lote va en
#: texto debajo (ver `_kt_lot_line`). Se conserva porque es pública.
KT_CODE_LOT = "lot"

#: Alto de la línea de texto «Lote: X» / «S/N: X», en mm. Solo se descuenta
#: del código de barras en las etiquetas que la llevan.
KT_LOT_LINE_MM = 3.0
#: Prefijo del lote o serie según `product.tracking`.
KT_LOT_PREFIXES = {"lot": "Lote:", "serial": "S/N:"}
#: Prefijo cuando llega un lote de un producto SIN seguimiento —pasa si se
#: cambió el seguimiento después de recibir—: no se sabe si era un lote o un
#: serial, así que no se elige.
KT_LOT_PREFIX_UNKNOWN = "Lote/S/N:"

#: Valor propio de `print_format` en el asistente nativo. Es la única vía por
#: la que el botón Imprimir llega a este informe.
KT_PRINT_FORMAT = "kt_label_grid_pdf"
#: El informe, tal como lo devuelve `_prepare_report_data`.
KT_REPORT_XMLID = "kt_label_printing.action_report_kt_label_grid"
KT_REPORT_NAME = "kt_label_printing.report_kt_label_grid_document"

#: Relleno interior de cada celda, en mm.
KT_CELL_PADDING_MM = 1.5
#: Alto reservado en la celda para el texto — nombre, código legible y
#: referencia, tres líneas pequeñas —, en mm. El código de barras ocupa lo
#: que queda, sin pasar de `content_size_mm`.
KT_TEXT_BAND_MM = 9.0
#: Por debajo de esta altura un lector no encuentra las barras.
KT_MIN_BARCODE_HEIGHT_MM = 3.0


def compute_label_geometry(size):
    """Geometría de la hoja a partir de un `kt.label.size`, toda en mm.

    Columnas y filas son los campos calculados del propio tamaño: la hoja es
    la que describe quien imprime, no una rejilla estándar. El código de
    barras mide `content_size_mm` de ancho, recortado a lo que cabe dentro de
    la celda, y de alto lo que deja libre la banda de texto, con el mismo
    tope.
    """
    inner_width = size.label_width_mm - 2 * KT_CELL_PADDING_MM
    inner_height = size.label_height_mm - 2 * KT_CELL_PADDING_MM
    barcode_width = max(0.0, min(size.content_size_mm, inner_width))
    barcode_height = min(size.content_size_mm, inner_height - KT_TEXT_BAND_MM)
    # La etiqueta de lote o serie lleva una línea más de texto. Solo ella
    # cede ese alto; las demás conservan su código tal cual.
    barcode_height_tracked = min(
        size.content_size_mm, inner_height - KT_TEXT_BAND_MM - KT_LOT_LINE_MM
    )
    return {
        "columns": size.columns,
        "rows": size.rows,
        "page_width_mm": size.page_width_mm,
        "page_height_mm": size.page_height_mm,
        "margin_mm": size.margin_mm,
        "cell_width_mm": size.label_width_mm,
        "cell_height_mm": size.label_height_mm,
        "cell_padding_mm": KT_CELL_PADDING_MM,
        "barcode_width_mm": barcode_width,
        "barcode_height_mm": max(KT_MIN_BARCODE_HEIGHT_MM, barcode_height),
        "barcode_height_tracked_mm": max(
            KT_MIN_BARCODE_HEIGHT_MM, barcode_height_tracked
        ),
    }


class ReportKtLabelGrid(models.AbstractModel):
    _name = "report.kt_label_printing.report_kt_label_grid_document"
    _description = "Etiqueta de producto en cuadrícula - PDF"

    def _kt_label_code(self, product):
        """Qué código imprimir para un producto, y de dónde sale.

        **Punto de extensión.** Es un método de modelo a propósito, no una
        función suelta: un módulo puente puede heredar este `AbstractModel`
        y sobrescribirlo sin que `kt_label_printing` tenga que conocerlo ni
        depender de él.

        Contrato, que es lo que ese puente debe respetar:

        - recibe **una** variante, ``product.product``: su ``barcode`` es
          el de la variante, no el de la plantilla;
        - devuelve una tupla ``(code, kind)``;
        - ``code`` es una cadena no vacía, o ``False`` si no hay ninguno;
        - ``kind`` es ``KT_CODE_BARCODE``, ``KT_CODE_SKU``, o ``False``
          cuando no hay código;
        - **nunca lanza**, y **nunca descarta la etiqueta**: un producto sin
          código sigue ocupando su celda, con su nombre y su referencia.

        Orden de respaldo, de más específico a menos:

        a) ``barcode`` del producto;
        b) si no lo hay, ``default_code`` — el SKU — impreso en Code128 y
           marcado como tal en la etiqueta;
        c) si no hay ninguno, etiqueta sin gráfico.

        Un puente que quiera imprimir códigos alternos se inserta **entre
        (a) y (b)**, llamando a ``super()`` para el resto:

            class ReportKtLabelGrid(models.AbstractModel):
                _inherit = "report.kt_label_printing.report_kt_label_grid_document"

                def _kt_label_code(self, product):
                    if not product.barcode and <hay alterno>:
                        return <alterno>, "alt"
                    return super()._kt_label_code(product)
        """
        if product.barcode:
            return product.barcode, KT_CODE_BARCODE
        if product.default_code:
            return product.default_code, KT_CODE_SKU
        return False, False

    def _kt_barcode_png(self, code):
        """La imagen Code128 de `code`, o ``False`` si no se puede codificar.

        `ir.actions.report.barcode()` **lanza** `ValueError("Cannot convert
        into barcode.")` cuando Code128 no puede codificar el valor — no
        degrada. Sin esta comprobación, un solo producto con un carácter
        fuera de rango, que en ferretería es perfectamente posible
        (``TORNILLO-Ñ``), **rompería el PDF del lote entero**, no su etiqueta.

        Se pregunta intentándolo, no adivinando por rango de caracteres: la
        autoridad sobre qué codifica Code128 es el propio renderizador. Y la
        imagen que sale de intentarlo **es la que se imprime**: la plantilla
        no la vuelve a pedir.
        """
        try:
            return self.env["ir.actions.report"].barcode(
                "Code128", code, width=600, height=100, humanreadable=0
            )
        except (ValueError, AttributeError):
            return False

    def _kt_printable_label_code(self, product, images=None):
        """**La** clasificación de una variante: ``(code, kind, reason)``.

        Es el único sitio donde se decide qué sale en una etiqueta. La usan
        el asistente —para el aviso—, el recuento del informe y la plantilla,
        y ninguno de ellos la repite.

        Envuelve a `_kt_label_code` en vez de mezclarse con él, para que un
        módulo puente solo tenga que sobrescribir la **elección** y herede
        la guarda sin saber que existe.

        Si el código elegido —venga de la rama que venga, incluido un
        `barcode` mal formado— no se puede codificar, **cae a (c)** con
        ``reason`` puesto, y el llamador lo cuenta y lo lista.

        Si se pasa ``images``, un diccionario, se deja en él la imagen ya
        generada, por código, para que quien imprime no la genere otra vez.
        """
        code, kind = self._kt_label_code(product)
        return self._kt_guard_code(code, kind, images)

    def _kt_guard_code(self, code, kind, images=None):
        """La guarda de codificación del código que se dibuja.

        Hasta 19.0.1.0.2 la usaban también los lotes, cuyo código era el
        gráfico. Desde 19.0.1.1.0 el lote va en texto y no pasa por aquí: un
        lote que Code128 no codifica ya no deja la etiqueta sin gráfico.
        """
        if not code:
            return False, False, False
        png = self._kt_barcode_png(code)
        if not png:
            return False, False, KT_REASON_UNENCODABLE
        if images is not None:
            images[code] = "data:image/png;base64,%s" % base64.b64encode(png).decode()
        return code, kind, False

    def _kt_lot_line(self, product, lot_code):
        """La línea de texto del lote o serie: ``(prefijo, valor)``.

        Decisión de Jonaily (DECISIONES, «Respuesta 4»): la etiqueta de un
        producto con lote o serie lleva **los dos** —el código del producto
        como gráfico y, debajo, el lote o serie en texto—. El nativo imprime
        solo el lote.

        El prefijo sale de `product.tracking`: «Lote:» o «S/N:». Si el
        producto no tiene seguimiento pero llega con lote, no se sabe cuál
        era y se usa «Lote/S/N:», que no afirma ninguno de los dos.

        **Solo texto, a propósito**: sin segundo código de barras. Quien
        necesite escanear el lote lo teclea.
        """
        prefix = KT_LOT_PREFIXES.get(product.tracking, KT_LOT_PREFIX_UNKNOWN)
        return prefix, lot_code

    def _kt_label_entries(self, data):
        """Qué se imprime y cuántas veces, leído como lo lee el nativo.

        Sigue a `product.report.product_label_report._prepare_data`: el
        modelo sale de ``active_model``; ``quantity_by_product`` da cuántas
        etiquetas por registro —con «cantidades de la operación», stock la
        rellena con lo recibido—; y ``custom_barcodes`` añade las de lote o
        serie, con su propio código. Las claves llegan como cadenas cuando
        los datos vuelven del navegador, y como enteros si no.

        Devuelve ``[(variante, cantidad, código_de_lote_o_False)]``, en el
        orden del nativo, por nombre. Una plantilla se expande en sus
        variantes, cada una con la cantidad de la plantilla: la etiqueta es
        de la variante.
        """
        model = data.get("active_model") or "product.product"
        if model not in ("product.product", "product.template"):
            raise UserError(
                _("Product model not defined, Please contact your administrator.")
            )
        Product = self.env[model].with_context(display_default_code=False)
        quantities = {
            int(key): int(qty)
            for key, qty in (data.get("quantity_by_product") or {}).items()
        }
        records = Product.search([("id", "in", list(quantities))], order="name, id")

        def variants_of(record):
            if record._name == "product.template":
                return record.product_variant_ids
            return record

        entries = []
        for record in records:
            for variant in variants_of(record):
                entries.append((variant, quantities[record.id], False))
        for key, codes in (data.get("custom_barcodes") or {}).items():
            variant = variants_of(Product.browse(int(key)))[:1]
            for code, qty in codes:
                entries.append((variant, int(qty), code))
        return entries

    def _get_report_values(self, docids, data):
        env = self.env
        size = env["kt.label.size"].browse(data.get("kt_label_size_id")).exists()
        if not size:
            raise UserError(
                _("Selecciona un tamaño de etiqueta para la rejilla PDF Kuvexta.")
            )
        geometry = compute_label_geometry(size)
        columns, rows = geometry["columns"], geometry["rows"]

        # Una sola clasificación por variante, no una por etiqueta ni por
        # lote: con tres unidades recibidas en dos lotes, la variante se
        # decide una vez y su imagen se genera una vez.
        images = {}
        codes = {}
        labels = []
        # Qué salió por cada rama, para poder decirlo y no dejar un hueco
        # silencioso. El SKU es legible y buscable, pero no es el EAN del
        # fabricante; y sin código no se puede escanear en absoluto.
        # Se cuenta POR PRODUCTO, también en las etiquetas de lote: es lo que
        # hace el aviso del asistente, y los dos tienen que decir lo mismo.
        as_sku = env["product.product"]
        without_code = env["product.product"]
        unencodable = env["product.product"]
        for product, qty, lot_code in self._kt_label_entries(data):
            # El gráfico es SIEMPRE el del producto, con su orden a/b/c; el
            # lote o serie, si lo hay, va en texto debajo.
            if product.id not in codes:
                codes[product.id] = self._kt_printable_label_code(product, images)
            resolved = codes[product.id]
            lot_line = self._kt_lot_line(product, lot_code) if lot_code else False
            _code, kind, reason = resolved
            if kind == KT_CODE_SKU:
                as_sku |= product
            elif reason == KT_REASON_UNENCODABLE:
                # Cae a (c), pero por un motivo distinto: tenía código y no
                # se puede imprimir. Quien reciba la mercancía debería
                # corregir ese dato, no resignarse.
                unencodable |= product
            elif not kind:
                without_code |= product
            labels.extend([(product, resolved, lot_line)] * qty)

        return {
            "labels": labels,
            "columns": columns,
            "rows": rows,
            "page_numbers": compute_page_numbers(len(labels), columns, rows),
            "kt_geometry": geometry,
            # Cada etiqueta lleva ya su clasificación y la imagen ya está
            # generada: la plantilla no decide nada ni llama al renderizador.
            "kt_codes": codes,
            "kt_barcode_images": images,
            "kt_code_sku": KT_CODE_SKU,
            # La hoja lleva SOLO etiquetas: en papel adhesivo cualquier aviso
            # impreso ocuparía celdas y desplazaría la cuadrícula. El recuento
            # viaja en los valores del informe; el aviso visible está en el
            # asistente, que es donde se mira antes de imprimir.
            "kt_printed_as_sku": as_sku,
            "kt_printed_as_sku_count": len(as_sku),
            "kt_without_code": without_code,
            "kt_without_code_count": len(without_code),
            "kt_unencodable": unencodable,
            "kt_unencodable_count": len(unencodable),
        }


class IrActionsReport(models.Model):
    """El tamaño de hoja de `kt.label.size`, aplicado al PDF.

    Columnas y filas se calculan para una hoja concreta —la de
    `kt.label.size`—, así que el PDF tiene que salir en esa hoja: si no, la
    rejilla no cabe y desborda a páginas que nadie pidió. El `paperformat` de
    Odoo es un registro estático, uno por informe, así que el tamaño se
    aplica al construir los argumentos de wkhtmltopdf y solo cuando el
    informe que se renderiza es éste y trae un tamaño.
    """

    _inherit = "ir.actions.report"

    def _render_qweb_pdf_prepare_streams(self, report_ref, data, res_ids=None):
        target = self
        report = self._get_report(report_ref)
        if report.report_name == KT_REPORT_NAME and data:
            size = self.env["kt.label.size"].browse(data.get("kt_label_size_id"))
            if size.exists():
                target = self.with_context(
                    kt_label_page_mm=(size.page_width_mm, size.page_height_mm)
                )
        return super(IrActionsReport, target)._render_qweb_pdf_prepare_streams(
            report_ref, data, res_ids=res_ids
        )

    @api.model
    def _build_wkhtmltopdf_args(
        self,
        paperformat_id,
        landscape,
        specific_paperformat_args=None,
        set_viewport_size=False,
    ):
        page = self.env.context.get("kt_label_page_mm")
        if page and paperformat_id:
            # Un registro en memoria, no uno guardado: el tamaño es de esta
            # impresión, no del informe.
            paperformat_id = paperformat_id.new(
                {
                    "name": paperformat_id.name,
                    "format": "custom",
                    "page_width": round(page[0]),
                    "page_height": round(page[1]),
                    "orientation": "Portrait",
                    "margin_top": 0,
                    "margin_bottom": 0,
                    "margin_left": 0,
                    "margin_right": 0,
                    "header_spacing": 0,
                    "header_line": False,
                    "dpi": paperformat_id.dpi or 96,
                    "disable_shrinking": True,
                }
            )
        return super()._build_wkhtmltopdf_args(
            paperformat_id,
            landscape,
            specific_paperformat_args=specific_paperformat_args,
            set_viewport_size=set_viewport_size,
        )
