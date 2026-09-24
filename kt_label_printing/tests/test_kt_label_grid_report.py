# -*- coding: utf-8 -*-
"""Pruebas del informe de etiquetas en cuadrícula.

Comprobaciones deterministas sobre cifras, dimensiones e identificadores, que
es lo que el criterio de aceptación del piloto exige: el veredicto tiene que
ser el mismo lo ejecute quien lo ejecute, no depender del juicio de nadie.

Las pruebas que de verdad cierran el asunto van **por la interfaz**: crean el
asistente con la opción «Rejilla PDF Kuvexta», pulsan Imprimir —`process()`—
y generan el PDF con lo que el botón devolvió, con el binario real, contando
sus páginas. Llamar al informe directamente probaría un informe al que nadie
llega.
"""

import io
import json
from types import SimpleNamespace
from unittest.mock import patch

from odoo import Command
from odoo.addons.kt_label_printing.models.kt_label_grid_utils import (
    compute_page_numbers,
)
from odoo.addons.kt_label_printing.report.kt_label_grid_report import (
    KT_CODE_BARCODE,
    KT_CODE_SKU,
    KT_PRINT_FORMAT,
    KT_REASON_UNENCODABLE,
)
from odoo.addons.kt_label_printing.report.kt_label_grid_report import (
    IrActionsReport as KtIrActionsReport,
)
from odoo.addons.kt_label_printing.report.kt_label_grid_report import (
    compute_label_geometry,
)
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, tagged
from odoo.tools.pdf import PdfFileReader

REPORT = "kt_label_printing.action_report_kt_label_grid"
REPORT_MODEL = "report.kt_label_printing.report_kt_label_grid_document"


def _blank_pdf():
    """Un PDF válido de una página A4 vacía, sin dependencias."""
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] >>",
    ]
    out = b"%PDF-1.4\n"
    offsets = []
    for number, body in enumerate(objects, 1):
        offsets.append(len(out))
        out += b"%d 0 obj\n%s\nendobj\n" % (number, body)
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1)
    out += b"".join(b"%010d 00000 n \n" % offset for offset in offsets)
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\n" % (len(objects) + 1)
    out += b"startxref\n%d\n%%%%EOF\n" % xref
    return out


@tagged("post_install", "-at_install")
class TestKtLabelGridReport(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # 4 columnas x 11 filas en A4: 44 por hoja.
        cls.size = cls.env["kt.label.size"].create(
            {
                "name": "Prueba 48x25 en A4",
                "label_width_mm": 48.0,
                "label_height_mm": 25.0,
                "content_size_mm": 18.0,
                "page_width_mm": 210.0,
                "page_height_mm": 297.0,
                "margin_mm": 5.0,
            }
        )
        # 2 columnas x 4 filas en A4: 8 por hoja.
        cls.big_size = cls.env["kt.label.size"].create(
            {
                "name": "Prueba 100x70 en A4",
                "label_width_mm": 100.0,
                "label_height_mm": 70.0,
                "content_size_mm": 60.0,
                "page_width_mm": 210.0,
                "page_height_mm": 297.0,
                "margin_mm": 5.0,
            }
        )
        cls.report = cls.env[REPORT_MODEL]

    def _product(self, name, code=None, barcode=None):
        return self.env["product.template"].create(
            {
                "name": name,
                "default_code": code,
                "barcode": barcode,
            }
        )

    def _batch(self, count, prefix="REF"):
        products = self.env["product.template"]
        for index in range(count):
            products |= self._product(
                "Artículo %s %02d" % (prefix, index),
                "%s-%02d" % (prefix, index),
                # Uno de cada cinco sin EAN, para que el PDF del lote
                # ejercite también la rama del SKU.
                False if index % 5 == 0 else "77%03d%06d" % (len(prefix), index),
            )
        return products

    def _wizard(self, products, size=None, copies=1):
        return self.env["product.label.layout"].create(
            {
                "print_format": KT_PRINT_FORMAT,
                "kt_label_size_id": (size or self.size).id,
                "custom_quantity": copies,
                "product_tmpl_ids": [(6, 0, products.ids)],
            }
        )

    @staticmethod
    def _as_sent_by_the_browser(data):
        """Los datos del informe tal como vuelven del navegador.

        El botón Imprimir entrega la acción al cliente web, que pide el PDF
        mandando `data` en JSON: las claves enteras llegan como cadenas.
        Pasarlos tal cual saldrían del asistente no es el camino real.
        """
        return json.loads(json.dumps(data))

    def _print(self, wizard):
        """Lo que hace el botón Imprimir, y el PDF que sale de ahí."""
        action = wizard.process()
        pdf_bytes, content_type = (
            self.env["ir.actions.report"]
            # Odoo devuelve HTML en lugar de PDF cuando corre con
            # `test_enable`, salvo que se pida `force_report_rendering`: sin
            # él estas pruebas no probarían lo que dicen probar.
            .with_context(force_report_rendering=True)._render_qweb_pdf(
                action["report_name"],
                data=self._as_sent_by_the_browser(action["data"]),
            )
        )
        self.assertEqual(content_type, "pdf")
        self.assertTrue(pdf_bytes.startswith(b"%PDF-"), "lo devuelto no es un PDF")
        return action, len(PdfFileReader(io.BytesIO(pdf_bytes), strict=False).pages)

    # --- geometría -----------------------------------------------------

    def test_grid_is_computed_from_the_configured_size(self):
        """Columnas y filas salen de las medidas, no de un número escrito."""
        self.assertEqual((self.size.columns, self.size.rows), (4, 11))
        self.assertEqual((self.big_size.columns, self.big_size.rows), (2, 4))
        usable_width = self.size.page_width_mm - 2 * self.size.margin_mm
        usable_height = self.size.page_height_mm - 2 * self.size.margin_mm
        self.assertLessEqual(self.size.columns * self.size.label_width_mm, usable_width)
        self.assertLessEqual(self.size.rows * self.size.label_height_mm, usable_height)

    def test_the_sheet_takes_its_geometry_from_the_label_size(self):
        """Columnas, filas, celda y código de barras, en mm de `kt.label.size`.

        Ni la rejilla estándar del asistente ni un 32x12 escrito en la
        plantilla: las medidas del HTML son las del tamaño elegido.
        """
        products = self._batch(3)
        wizard = self._wizard(products)
        values = self.report._get_report_values(
            products.ids, wizard._prepare_report_data()[1]
        )
        geometry = compute_label_geometry(self.size)
        self.assertEqual((values["columns"], values["rows"]), (4, 11))
        self.assertEqual(values["kt_geometry"], geometry)
        self.assertEqual(geometry["cell_width_mm"], 48.0)
        self.assertEqual(geometry["cell_height_mm"], 25.0)
        # 18 de contenido cabe a lo ancho; a lo alto lo recorta la banda de
        # texto: 25 - 2 x 1,5 de relleno - 9 = 13.
        self.assertEqual(geometry["barcode_width_mm"], 18.0)
        self.assertEqual(geometry["barcode_height_mm"], 13.0)
        big = compute_label_geometry(self.big_size)
        self.assertEqual((big["barcode_width_mm"], big["barcode_height_mm"]), (60, 58))

        html = (
            self.env["ir.actions.report"]
            ._render_qweb_html(REPORT, products.ids, data=wizard.process()["data"])[0]
            .decode()
        )
        self.assertIn("width:48.0mm; height:25.0mm", html)
        self.assertIn("width:18.0mm; height:13.0mm", html)
        self.assertNotIn("width:32mm", html, "no queda el tamaño fijo de antes")

    def test_missing_size_is_refused_instead_of_guessed(self):
        """Sin tamaño no hay geometría: se pide, no se inventa."""
        products = self._batch(1)
        wizard = self._wizard(products)
        wizard.kt_label_size_id = False
        with self.assertRaises(UserError):
            wizard.process()

    # --- paginación ----------------------------------------------------

    def test_page_count_is_exact_at_the_boundaries(self):
        """Una hoja justa no abre una segunda; una etiqueta más, sí."""
        self.assertEqual(compute_page_numbers(0, 4, 10), 0)
        self.assertEqual(compute_page_numbers(1, 4, 10), 1)
        self.assertEqual(compute_page_numbers(40, 4, 10), 1)
        self.assertEqual(compute_page_numbers(41, 4, 10), 2)
        self.assertEqual(compute_page_numbers(80, 4, 10), 2)
        self.assertEqual(compute_page_numbers(81, 4, 10), 3)

    def test_copies_repeat_each_product_in_the_batch(self):
        products = self._product("A", "A-1", "7700000000017") + self._product(
            "B", "B-1", "7700000000024"
        )
        labels = self.report._get_report_values(
            products.ids, self._wizard(products, copies=3)._prepare_report_data()[1]
        )["labels"]
        self.assertEqual(len(labels), 6)
        first = products[0].product_variant_id
        self.assertEqual(sum(1 for label in labels if label[0] == first), 3)

    # --- el punto de extensión, una prueba por rama ---------------------

    def test_branch_a_uses_the_official_barcode(self):
        product = self._product("Con EAN", "A-2", "7700000000031").product_variant_id
        self.assertEqual(
            self.report._kt_label_code(product), ("7700000000031", KT_CODE_BARCODE)
        )

    def test_branch_b_falls_back_to_the_sku(self):
        """Sin barcode pero con referencia: se imprime el SKU, marcado."""
        product = self._product(
            "Tornillo suelto 1/4", "FER-TOR-0014", False
        ).product_variant_id
        self.assertEqual(
            self.report._kt_label_code(product), ("FER-TOR-0014", KT_CODE_SKU)
        )

    def test_branch_c_has_no_code_at_all(self):
        """Sin ninguno: no se omite, sale sin gráfico."""
        product = self._product(
            "Cable cortado a medida", False, False
        ).product_variant_id
        self.assertEqual(self.report._kt_label_code(product), (False, False))
        self.assertEqual(
            self.report._kt_printable_label_code(product), (False, False, False)
        )

    def test_the_barcode_wins_over_the_sku(self):
        """El orden importa: (a) antes que (b), no al revés."""
        product = self._product(
            "Ambos", "REF-AMBOS", "7700000000048"
        ).product_variant_id
        code, kind = self.report._kt_label_code(product)
        self.assertEqual(code, "7700000000048")
        self.assertEqual(kind, KT_CODE_BARCODE)

    def test_no_product_is_ever_dropped_from_the_batch(self):
        con = self._product("Con EAN", "C-1", "7700000000055")
        sku = self._product("Solo SKU", "S-1", False)
        nada = self._product("Sin nada", False, False)
        products = con + sku + nada
        labels = self.report._get_report_values(
            products.ids, self._wizard(products)._prepare_report_data()[1]
        )["labels"]
        self.assertEqual(len(labels), 3, "ninguna rama descarta la etiqueta")

    # --- la guarda de codificación --------------------------------------

    def test_an_unencodable_code_falls_to_c_instead_of_breaking(self):
        """Un código que Code128 no puede codificar cae a (c), con motivo.

        `barcode()` lanza en vez de degradar, así que sin guarda un solo
        producto con un carácter fuera de rango rompería el PDF del lote
        entero — no su etiqueta, el lote.
        """
        raro = self._product(
            "Tornillo especial", "TORNILLO-Ñ", False
        ).product_variant_id
        code, kind, reason = self.report._kt_printable_label_code(raro)
        self.assertFalse(code, "no debe imprimirse un código que no codifica")
        self.assertFalse(kind)
        self.assertEqual(reason, KT_REASON_UNENCODABLE)
        # La elección cruda sí lo eligió: la guarda es lo que lo detiene.
        self.assertEqual(self.report._kt_label_code(raro), ("TORNILLO-Ñ", KT_CODE_SKU))

    def test_a_malformed_barcode_also_falls_to_c(self):
        """La guarda vale para cualquier rama, no solo para el SKU."""
        malo = self._product("Con EAN roto", "M-1", "EAN-ROTO-Ñ").product_variant_id
        code, kind, reason = self.report._kt_printable_label_code(malo)
        self.assertFalse(code)
        self.assertFalse(kind, "cae a (c), no se queda en la rama del barcode")
        self.assertEqual(reason, KT_REASON_UNENCODABLE)

    def test_the_batch_still_prints_with_an_unencodable_product_in_it(self):
        """El PDF del lote sale igual, y ese producto aparece como (c)."""
        buenos = self.env["product.template"]
        for index in range(4):
            buenos |= self._product(
                "Bueno %d" % index, "OK-%d" % index, "77000000001%02d" % index
            )
        raro = self._product("Tornillo especial", "TORNILLO-Ñ", False)
        products = buenos + raro
        wizard = self._wizard(products)

        values = self.report._get_report_values(
            products.ids, wizard._prepare_report_data()[1]
        )
        self.assertEqual(values["kt_unencodable_count"], 1)
        self.assertEqual(values["kt_unencodable"], raro.product_variant_id)
        self.assertEqual(values["kt_without_code_count"], 0, "no es el mismo caso")
        self.assertEqual(len(values["labels"]), 5, "nadie se queda sin etiqueta")

        _action, pages = self._print(wizard)
        self.assertEqual(pages, 1, "el lote entero imprime pese al código imposible")

    # --- una sola clasificación, una sola imagen ------------------------

    def test_each_product_is_classified_and_drawn_once(self):
        """Tres copias no son tres clasificaciones ni tres imágenes.

        El recuento, la plantilla y la guarda comparten la misma
        clasificación, y la imagen que genera la guarda es la que se
        imprime: el renderizador de códigos se llama una vez por producto
        con código, al construir los valores, y ninguna al dibujar.
        """
        con = self._product("Con EAN", "D-1", "7700000000611")
        sku = self._product("Solo SKU", "D-2", False)
        nada = self._product("Sin nada", False, False)
        products = con + sku + nada
        wizard = self._wizard(products, copies=3)
        data = wizard.process()["data"]

        report_class = type(self.env["ir.actions.report"])
        original = report_class.barcode
        drawn = []

        def counting(report, barcode_type, value, **kwargs):
            drawn.append(value)
            return original(report, barcode_type, value, **kwargs)

        with patch.object(report_class, "barcode", counting):
            html = self.env["ir.actions.report"]._render_qweb_html(
                REPORT, products.ids, data=data
            )[0]

        self.assertEqual(sorted(drawn), sorted(["7700000000611", "D-2"]))
        self.assertEqual(html.count(b"data:image/png;base64,"), 6, "3 copias x 2")
        self.assertNotIn(b"/report/barcode", html, "ninguna imagen se pide aparte")

    # --- el recuento ----------------------------------------------------

    def test_report_values_count_what_went_out_by_each_branch(self):
        """El recuento viaja en los valores, no impreso en la hoja.

        La hoja lleva solo etiquetas: en papel adhesivo un aviso impreso
        ocuparía celdas y desplazaría la cuadrícula. El asistente es donde
        se mira antes de imprimir.
        """
        con = self._product("Con EAN", "C-9", "7700000000109")
        sku_a = self._product("Tornillo suelto 3/8", "T-9", False)
        sku_b = self._product("Arandela 5mm", "A-9", False)
        nada = self._product("Cable cortado a medida", False, False)
        products = con + sku_a + sku_b + nada
        values = self.report._get_report_values(
            products.ids, self._wizard(products)._prepare_report_data()[1]
        )
        self.assertEqual(values["kt_printed_as_sku_count"], 2)
        self.assertEqual(
            values["kt_printed_as_sku"], (sku_a + sku_b).product_variant_ids
        )
        self.assertEqual(values["kt_without_code_count"], 1)
        self.assertEqual(values["kt_without_code"], nada.product_variant_id)
        self.assertNotIn(con.product_variant_id, values["kt_printed_as_sku"])
        self.assertNotIn(con.product_variant_id, values["kt_without_code"])
        self.assertEqual(
            values["kt_codes"][sku_a.product_variant_id.id],
            ("T-9", KT_CODE_SKU, False),
        )

    # --- por la interfaz: el botón Imprimir ------------------------------

    def test_the_print_button_reaches_the_grid_and_prints_a_real_pdf(self):
        """Asistente con la opción propia → Imprimir → este informe → PDF.

        El lote llena **más de una hoja** a propósito: con 44 por hoja y 45
        etiquetas tienen que salir 2 páginas. Es la comprobación que
        distingue un informe que se alcanza y renderiza de uno que solo está
        declarado.
        """
        report = self.env.ref(REPORT)
        per_sheet = self.size.columns * self.size.rows
        products = self._batch(per_sheet + 1)
        wizard = self._wizard(products)
        self.assertEqual((wizard.columns, wizard.rows), (4, 11))

        action, pages = self._print(wizard)

        self.assertEqual(action["type"], "ir.actions.report")
        self.assertEqual(action["report_name"], report.report_name)
        self.assertEqual(action["report_type"], "qweb-pdf")
        self.assertEqual(action["data"]["kt_label_size_id"], self.size.id)
        self.assertEqual(pages, compute_page_numbers(len(products), 4, 11))
        self.assertEqual(pages, 2, "una etiqueta más que una hoja abre la segunda")

    def test_a_standard_format_still_prints_the_native_report(self):
        """La opción propia no secuestra a las demás."""
        products = self._batch(2)
        wizard = self._wizard(products)
        wizard.print_format = "4x12"
        xml_id, _data = wizard._prepare_report_data()
        self.assertEqual(xml_id, "product.report_product_template_label_4x12_noprice")

    def test_two_sizes_give_different_sheets(self):
        """Mismo lote, dos tamaños: distinto número por hoja y de páginas.

        12 etiquetas caben en una hoja de 48x25 (44 por hoja) y necesitan
        dos de 100x70 (8 por hoja). Si el informe siguiera usando una
        rejilla fija, las dos impresiones serían iguales.
        """
        products = self._batch(12, prefix="TAM")

        small = self._wizard(products, size=self.size)
        big = self._wizard(products, size=self.big_size)
        self.assertEqual(small.columns * small.rows, 44)
        self.assertEqual(big.columns * big.rows, 8)

        _action, small_pages = self._print(small)
        _action, big_pages = self._print(big)
        self.assertEqual(small_pages, 1)
        self.assertEqual(big_pages, 2)

    # --- el filtro del tamaño de hoja -----------------------------------

    def _capture_wkhtmltopdf_args(self):
        """Registra cada llamada a `_build_wkhtmltopdf_args`.

        Por cada una guarda los argumentos que salieron, los que habría
        dado Odoo **sin este módulo** —la misma llamada contra el siguiente
        de la cadena de herencia, saltándose solo la sobrescritura propia— y
        el tamaño de hoja que había en el contexto.
        """
        report_class = type(self.env["ir.actions.report"])
        original = report_class._build_wkhtmltopdf_args
        mro = report_class.__mro__
        # La implementación que viene justo después de la propia: es lo que
        # ejecutaría Odoo si este módulo no la sobrescribiera.
        without_this_module = next(
            klass.__dict__["_build_wkhtmltopdf_args"]
            for klass in mro[mro.index(KtIrActionsReport) + 1 :]
            if "_build_wkhtmltopdf_args" in klass.__dict__
        )
        calls = []

        def capturing(
            report,
            paperformat_id,
            landscape,
            specific_paperformat_args=None,
            set_viewport_size=False,
        ):
            args = original(
                report,
                paperformat_id,
                landscape,
                specific_paperformat_args=specific_paperformat_args,
                set_viewport_size=set_viewport_size,
            )
            without_module = without_this_module(
                report,
                paperformat_id,
                landscape,
                specific_paperformat_args=specific_paperformat_args,
                set_viewport_size=set_viewport_size,
            )
            calls.append(
                {
                    "args": args,
                    "without_module": without_module,
                    "page": report.env.context.get("kt_label_page_mm"),
                }
            )
            return args

        return patch.object(report_class, "_build_wkhtmltopdf_args", capturing), calls

    def _print_native_4x12(self, products, extra_data=None):
        """El informe nativo de etiquetas 4x12, por el botón Imprimir."""
        wizard = self.env["product.label.layout"].create(
            {
                "print_format": "4x12",
                "custom_quantity": 1,
                "product_tmpl_ids": [(6, 0, products.ids)],
            }
        )
        action = wizard.process()
        self.assertEqual(
            action["report_name"],
            self.env.ref(
                "product.report_product_template_label_4x12_noprice"
            ).report_name,
        )
        data = self._as_sent_by_the_browser(dict(action["data"], **(extra_data or {})))

        # El binario NO se ejecuta para el nativo: su plantilla carga los
        # assets CSS por HTTP desde el servidor de pruebas, que espera el
        # cursor de esta transacción mientras ella espera a wkhtmltopdf.
        # En el CI eso quedó colgado hasta cancelarlo. Lo que se prueba son
        # los argumentos, que se construyen antes; se sustituye solo la
        # ejecución, que los recibe y deja un PDF de una página vacía.
        received = []

        def fake_wkhtmltopdf(args):
            received.append(args)
            with open(args[-1], "wb") as pdf_file:
                pdf_file.write(_blank_pdf())
            return SimpleNamespace(returncode=0, stderr="")

        with patch(
            "odoo.addons.base.models.ir_actions_report._run_wkhtmltopdf",
            fake_wkhtmltopdf,
        ):
            pdf_bytes, content_type = (
                self.env["ir.actions.report"]
                .with_context(force_report_rendering=True)
                ._render_qweb_pdf(action["report_name"], data=data)
            )
        self.assertEqual(content_type, "pdf")
        self.assertTrue(pdf_bytes.startswith(b"%PDF-"))
        self.assertTrue(received, "el nativo tiene que llegar hasta wkhtmltopdf")
        return received

    def test_the_native_4x12_report_gets_exactly_odoo_arguments(self):
        """El informe nativo recibe lo mismo que en un Odoo sin este módulo.

        Para que la prueba muerda, a los datos del nativo se les añade un
        `kt_label_size_id`: lo único que impide entonces aplicarle la hoja
        de la rejilla es el filtro por `report_name`. Si el filtro se
        rompiera, aparecerían `--page-width`/`--page-height` propios.
        """
        products = self._batch(3, prefix="NAT")
        patcher, calls = self._capture_wkhtmltopdf_args()
        with patcher:
            received = self._print_native_4x12(
                products, extra_data={"kt_label_size_id": self.big_size.id}
            )

        self.assertTrue(calls, "el nativo tiene que pasar por wkhtmltopdf")
        self.assertEqual(len(received), len(calls))
        for sent, call in zip(received, calls):
            self.assertEqual(sent[: len(call["args"])], call["args"])
            self.assertNotIn("--page-width", sent)
            self.assertNotIn("--page-height", sent)
        for call in calls:
            self.assertIsNone(call["page"], "el nativo no recibe tamaño de hoja")
            self.assertEqual(
                call["args"],
                call["without_module"],
                "argumentos idénticos a los de Odoo sin este módulo",
            )
            self.assertNotIn("--page-width", call["args"])
            self.assertNotIn("--page-height", call["args"])

    def test_the_page_size_context_does_not_outlive_the_grid(self):
        """El tamaño de hoja vive solo mientras se imprime la rejilla.

        Se imprime la rejilla —que sí lleva su hoja, 210 x 297 mm— y
        después, en la misma transacción, el nativo 4x12: el contexto
        `kt_label_page_mm` no queda puesto en el entorno de la prueba ni
        llega a la segunda impresión.
        """
        products = self._batch(3, prefix="CTX")
        patcher, calls = self._capture_wkhtmltopdf_args()
        with patcher:
            self._print(self._wizard(products))
            grid_calls = list(calls)
            self.assertNotIn("kt_label_page_mm", self.env.context)
            self.assertNotIn(
                "kt_label_page_mm", self.env["ir.actions.report"].env.context
            )
            del calls[:]
            self._print_native_4x12(products)

        self.assertTrue(grid_calls)
        for call in grid_calls:
            self.assertEqual(call["page"], (210.0, 297.0))
            args = call["args"]
            self.assertEqual(args[args.index("--page-width") + 1], "210mm")
            self.assertEqual(args[args.index("--page-height") + 1], "297mm")
            self.assertNotIn("--page-size", args)

        self.assertTrue(calls, "el nativo tiene que pasar por wkhtmltopdf")
        for call in calls:
            self.assertIsNone(call["page"], "el contexto no sobrevive a la rejilla")
            self.assertEqual(call["args"], call["without_module"])
            self.assertNotIn("--page-width", call["args"])

    # --- recepción y variantes --------------------------------------------

    def _two_variants(self, name, code, eans):
        """Una plantilla con dos variantes, cada una con SU código de barras."""
        attribute = self.env["product.attribute"].create(
            {
                "name": "Medida %s" % name,
                "create_variant": "always",
                "value_ids": [
                    Command.create({"name": "1/4"}),
                    Command.create({"name": "3/8"}),
                ],
            }
        )
        template = self.env["product.template"].create(
            {
                "name": name,
                "attribute_line_ids": [
                    Command.create(
                        {
                            "attribute_id": attribute.id,
                            "value_ids": [Command.set(attribute.value_ids.ids)],
                        }
                    )
                ],
            }
        )
        variants = template.product_variant_ids
        self.assertEqual(len(variants), 2)
        for variant, suffix, ean in zip(variants, ("14", "38"), eans):
            variant.write({"default_code": "%s-%s" % (code, suffix), "barcode": ean})
        return template, variants

    def _labels_by_code(self, html):
        """Cuántas etiquetas llevan cada código impreso en texto."""
        return lambda code: html.count(("<span>%s</span>" % code).encode())

    def test_a_receipt_prints_one_label_per_received_unit_of_each_variant(self):
        """Recepción → Imprimir etiquetas → cantidades de la operación → PDF.

        Dos variantes del mismo tornillo, cada una con su EAN, reciben 3 y 5;
        una arandela sin EAN y con SKU recibe 2. Son 10 etiquetas: 3 con el
        EAN de una variante, 5 con el de la otra, y 2 con el SKU marcado.

        El asistente se abre como lo abre el botón de la recepción, con su
        contexto: sus variantes, sus movimientos y «cantidades de la
        operación». Las cantidades las construye stock, no este módulo.
        """
        _template, (small, big) = self._two_variants(
            "Tornillo hexagonal", "TOR-HEX", ("7701234500014", "7701234500038")
        )
        washer = self._product("Arandela plana", "ARA-PLA-05", False)
        washer = washer.product_variant_id
        supplier = self.env.ref("stock.stock_location_suppliers")
        stock = self.env.ref("stock.stock_location_stock")
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.env.ref("stock.picking_type_in").id,
                "location_id": supplier.id,
                "location_dest_id": stock.id,
                "move_ids": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "product_uom_qty": qty,
                            "product_uom": product.uom_id.id,
                            "location_id": supplier.id,
                            "location_dest_id": stock.id,
                        }
                    )
                    for product, qty in ((small, 3), (big, 5), (washer, 2))
                ],
            }
        )
        picking.action_confirm()
        self.assertEqual(picking.picking_type_code, "incoming")

        opened = picking.action_open_label_layout()
        wizard = (
            self.env["product.label.layout"]
            .with_context(**opened["context"])
            .create({"print_format": KT_PRINT_FORMAT, "kt_label_size_id": self.size.id})
        )
        self.assertEqual(wizard.move_quantity, "move")
        self.assertEqual(wizard.product_ids, small + big + washer)

        action = wizard.process()
        self.assertEqual(action["report_name"], self.env.ref(REPORT).report_name)
        data = self._as_sent_by_the_browser(action["data"])
        self.assertEqual(
            data["quantity_by_product"],
            {str(small.id): 3, str(big.id): 5, str(washer.id): 2},
            "las cantidades son las de stock, por variante",
        )

        values = self.report._get_report_values([], data)
        self.assertEqual(len(values["labels"]), 10)
        self.assertEqual(values["kt_codes"][small.id][:2], ("7701234500014", "barcode"))
        self.assertEqual(values["kt_codes"][big.id][:2], ("7701234500038", "barcode"))
        self.assertEqual(values["kt_codes"][washer.id][:2], ("ARA-PLA-05", KT_CODE_SKU))
        self.assertEqual(values["kt_printed_as_sku"], washer)

        html = self.env["ir.actions.report"]._render_qweb_html(
            action["report_name"], [], data=data
        )[0]
        printed = self._labels_by_code(html)
        self.assertEqual(printed("7701234500014"), 3, "cada variante con SU EAN")
        self.assertEqual(printed("7701234500038"), 5, "cada variante con SU EAN")
        self.assertEqual(printed("ARA-PLA-05"), 2)
        self.assertEqual(html.count(b">SKU</span>"), 2, "el SKU va marcado")

        _action, pages = self._print(wizard)
        self.assertEqual(pages, 1, "10 etiquetas caben en una hoja de 44")

    def test_printing_from_a_template_keeps_each_variant_barcode(self):
        """Desde la plantilla también: sus variantes, cada una con su código.

        La plantilla de dos variantes no tiene `barcode` propio; imprimir la
        plantilla daría SKU o nada. Se imprimen sus variantes, cada una con
        la cantidad de la plantilla.
        """
        template, (small, big) = self._two_variants(
            "Perno de anclaje", "PER-ANC", ("7701234500113", "7701234500137")
        )
        self.assertFalse(template.barcode)
        wizard = self._wizard(template, copies=2)
        data = self._as_sent_by_the_browser(wizard.process()["data"])
        self.assertEqual(data["active_model"], "product.template")

        values = self.report._get_report_values([], data)
        self.assertEqual(len(values["labels"]), 4)
        self.assertEqual(values["kt_codes"][small.id][0], "7701234500113")
        self.assertEqual(values["kt_codes"][big.id][0], "7701234500137")
        self.assertFalse(values["kt_printed_as_sku"])

    # --- lotes y números de serie -------------------------------------------
    #
    # Decisión de Jonaily (DECISIONES, «Respuesta 4»): la etiqueta de un
    # producto con lote o serie lleva LOS DOS — el código del producto, con su
    # orden a/b/c de siempre, y debajo, en texto, «Lote: X» o «S/N: X». El
    # nativo imprime solo el lote.
    #
    # Todo entra por el camino real: la recepción, el selector «¿Qué
    # etiquetas?» con «Etiquetas de producto», el asistente con «cantidades de
    # la operación» y la Rejilla PDF Kuvexta. Las cantidades y los lotes los
    # construye stock (`custom_barcodes`), no este módulo.

    def _tracked(self, name, code, barcode, tracking):
        """Un producto almacenable con seguimiento, en Unidades.

        En Unidades a propósito: con otra unidad, stock imprime una sola
        etiqueta y sin lote.
        """
        template = self._product(name, code, barcode)
        template.write({"is_storable": True, "tracking": tracking})
        return template.product_variant_id

    def _receipt(self, lines):
        """Una recepción confirmada con sus líneas ya hechas.

        ``lines`` es ``[(producto, [(lote_o_False, cantidad), ...])]``. Las
        líneas de movimiento se escriben explícitas, con su cantidad: stock
        solo emite `custom_barcodes` si hay cantidad hecha, y sin eso no
        saldría ningún lote.
        """
        supplier = self.env.ref("stock.stock_location_suppliers")
        stock = self.env.ref("stock.stock_location_stock")
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.env.ref("stock.picking_type_in").id,
                "location_id": supplier.id,
                "location_dest_id": stock.id,
                "move_ids": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "product_uom_qty": sum(qty for _lot, qty in done),
                            "product_uom": product.uom_id.id,
                            "location_id": supplier.id,
                            "location_dest_id": stock.id,
                        }
                    )
                    for product, done in lines
                ],
            }
        )
        picking.action_confirm()
        for move, (product, done) in zip(picking.move_ids, lines):
            self.assertEqual(move.product_id, product)
            move.move_line_ids = [Command.clear()] + [
                Command.create(
                    {
                        "product_id": product.id,
                        "product_uom_id": product.uom_id.id,
                        "location_id": supplier.id,
                        "location_dest_id": stock.id,
                        "picking_id": picking.id,
                        "lot_name": lot or False,
                        "quantity": qty,
                    }
                )
                for lot, qty in done
            ]
        return picking

    def _receipt_wizard(self, picking, size=None):
        """El asistente como lo abre la recepción: selector, luego productos.

        El botón «Imprimir etiquetas» de la recepción abre primero
        `picking.label.type`; con «Etiquetas de producto» —el valor por
        defecto— llama a `action_open_label_layout()`. Con «Etiquetas de
        lote/SN» iría a `lot.label.layout`, que este módulo no toca.
        """
        chooser = self.env["picking.label.type"].create(
            {"picking_ids": [Command.set(picking.ids)], "label_type": "products"}
        )
        opened = chooser.process()
        self.assertEqual(opened["res_model"], "product.label.layout")
        wizard = (
            self.env["product.label.layout"]
            .with_context(**opened["context"])
            .create(
                {
                    "print_format": KT_PRINT_FORMAT,
                    "kt_label_size_id": (size or self.size).id,
                }
            )
        )
        self.assertEqual(wizard.move_quantity, "move")
        return wizard

    def _jonaily_receipt(self):
        """La recepción de la decisión: lote 3+2, serie 1+1, sin seguimiento 2.

        La arandela va sin EAN y con SKU, para que la misma recepción
        ejercite también la rama (b) y el recuento.
        """
        screw = self._tracked("Tornillo con lote", "TOR-LOT", "7701234500212", "lot")
        drill = self._tracked("Taladro con serie", "TAL-SN", "7701234500229", "serial")
        washer = self._product("Arandela sin seguimiento", "ARA-SS-02", False)
        washer = washer.product_variant_id
        picking = self._receipt(
            [
                (screw, [("LOT-A", 3), ("LOT-B", 2)]),
                (drill, [("SN-0001", 1), ("SN-0002", 1)]),
                (washer, [(False, 2)]),
            ]
        )
        return picking, screw, drill, washer

    def _render(self, data):
        return self.env["ir.actions.report"]._render_qweb_html(REPORT, [], data=data)[0]

    @staticmethod
    def _lot_lines(html):
        """Cuántas etiquetas llevan cada texto de lote o serie, como línea."""
        return lambda text: html.count((">%s</div>" % text).encode())

    def test_stock_builds_lots_and_serials_without_counting_them_twice(self):
        """Las cantidades las construye stock, y un lote no se cuenta dos veces.

        Las líneas con lote van a `custom_barcodes` y NO suman en
        `quantity_by_product`: si lo hicieran saldrían 16 etiquetas, no 9.
        """
        picking, screw, drill, washer = self._jonaily_receipt()
        data = self._as_sent_by_the_browser(
            self._receipt_wizard(picking).process()["data"]
        )
        self.assertEqual(data["quantity_by_product"], {str(washer.id): 2})
        self.assertEqual(
            data["custom_barcodes"],
            {
                str(screw.id): [["LOT-A", 3], ["LOT-B", 2]],
                str(drill.id): [["SN-0001", 1], ["SN-0002", 1]],
            },
        )

    def test_every_label_carries_the_product_code_and_the_lot_below(self):
        """9 etiquetas, todas con el código del producto; el lote, debajo.

        El gráfico es el del producto —el EAN del tornillo, el del taladro,
        el SKU marcado de la arandela—, nunca el del lote. El lote o serie va
        en texto, con «Lote:» o «S/N:» según `product.tracking`.
        """
        picking, _screw, _drill, _washer = self._jonaily_receipt()
        data = self._as_sent_by_the_browser(
            self._receipt_wizard(picking).process()["data"]
        )
        values = self.report._get_report_values([], data)
        self.assertEqual(len(values["labels"]), 9)

        html = self._render(data)
        printed = self._labels_by_code(html)
        self.assertEqual(printed("7701234500212"), 5, "el tornillo, en sus 5 etiquetas")
        self.assertEqual(printed("7701234500229"), 2, "el taladro, en sus 2 etiquetas")
        self.assertEqual(printed("ARA-SS-02"), 2)
        self.assertEqual(html.count(b">SKU</span>"), 2, "el SKU va marcado")
        for lot in ("LOT-A", "LOT-B", "SN-0001", "SN-0002"):
            self.assertEqual(
                printed(lot), 0, "%s no es el código de ninguna etiqueta" % lot
            )

        lot_line = self._lot_lines(html)
        self.assertEqual(lot_line("Lote: LOT-A"), 3)
        self.assertEqual(lot_line("Lote: LOT-B"), 2)
        self.assertEqual(lot_line("S/N: SN-0001"), 1)
        self.assertEqual(lot_line("S/N: SN-0002"), 1)
        self.assertEqual(
            html.count(b'class="kt-label-lot"'), 7, "la arandela no lleva línea de lote"
        )

    def test_the_warning_and_the_count_agree_for_a_lot_product(self):
        """El aviso y el recuento clasifican por producto, y dicen lo mismo.

        Un producto con lote y sin EAN sale con el SKU. El aviso del
        asistente lo nombra; el recuento del informe también, UNA vez, no una
        por lote. Antes de este cambio el recuento contaba el lote y no el
        producto, y los dos no coincidían.
        """
        nails = self._tracked("Clavo por lotes", "CLA-LOT", False, "lot")
        picking = self._receipt([(nails, [("L-1", 4), ("L-2", 1)])])
        wizard = self._receipt_wizard(picking)
        self.assertIn("CLA-LOT", wizard.kt_label_code_warning)
        self.assertIn("con el SKU", wizard.kt_label_code_warning)

        data = self._as_sent_by_the_browser(wizard.process()["data"])
        values = self.report._get_report_values([], data)
        self.assertEqual(values["kt_printed_as_sku"], nails)
        self.assertEqual(values["kt_printed_as_sku_count"], 1)
        self.assertEqual(len(values["labels"]), 5)

    def test_a_product_with_several_lots_is_drawn_once(self):
        """Una imagen por producto, no por lote: 3 imágenes para 9 etiquetas."""
        picking, _screw, _drill, _washer = self._jonaily_receipt()
        data = self._as_sent_by_the_browser(
            self._receipt_wizard(picking).process()["data"]
        )
        report_class = type(self.env["ir.actions.report"])
        original = report_class.barcode
        drawn = []

        def counting(report, barcode_type, value, **kwargs):
            drawn.append(value)
            return original(report, barcode_type, value, **kwargs)

        with patch.object(report_class, "barcode", counting):
            html = self._render(data)

        self.assertEqual(
            sorted(drawn), sorted(["7701234500212", "7701234500229", "ARA-SS-02"])
        )
        self.assertEqual(html.count(b"data:image/png;base64,"), 9)

    def test_labels_without_lot_keep_their_geometry(self):
        """La línea de lote resta sitio solo a las etiquetas que la llevan.

        Con 48x25 el código mide 13 mm; en las de lote o serie, 10 mm, para
        dejar sitio a la cuarta línea. La arandela conserva sus 13 mm.
        """
        geometry = compute_label_geometry(self.size)
        self.assertEqual(geometry["barcode_height_mm"], 13.0)
        self.assertEqual(geometry["barcode_height_tracked_mm"], 10.0)

        picking, _screw, _drill, _washer = self._jonaily_receipt()
        data = self._as_sent_by_the_browser(
            self._receipt_wizard(picking).process()["data"]
        )
        html = self._render(data)
        self.assertEqual(html.count(b"height:13.0mm;"), 2, "la arandela, sin cambio")
        self.assertEqual(html.count(b"height:10.0mm;"), 7, "las 7 de lote o serie")

    def test_a_receipt_with_lots_prints_the_right_pages(self):
        """PDF real: 9 etiquetas son 1 hoja de 44 y 2 hojas de 8.

        Con 8 por hoja la novena etiqueta abre la segunda página: el límite
        de página se ejercita con etiquetas de lote, y la línea extra no
        empuja la cuadrícula a otra hoja.
        """
        picking, _screw, _drill, _washer = self._jonaily_receipt()
        _action, pages = self._print(self._receipt_wizard(picking))
        self.assertEqual(pages, 1, "9 etiquetas caben en una hoja de 44")
        _action, pages = self._print(self._receipt_wizard(picking, self.big_size))
        self.assertEqual(pages, 2, "con 8 por hoja, la novena abre la segunda")

    def test_a_long_lot_is_clipped_without_breaking_the_grid(self):
        """Un lote que no cabe se recorta a la vista y no mueve la cuadrícula.

        La línea lleva `text-overflow:ellipsis` dentro de una celda de tamaño
        fijo con `overflow:hidden`: el recorte se ve y nada desborda. Que se
        LEA bien en papel se comprueba a ojo en el ensayo.
        """
        long_lot = "L-" + "PROVEEDOR-EXTRANJERO-" * 6
        bolts = self._tracked("Perno de lote largo", "PER-LAR", "7701234500236", "lot")
        picking = self._receipt([(bolts, [(long_lot, 9)])])
        data = self._as_sent_by_the_browser(
            self._receipt_wizard(picking, self.big_size).process()["data"]
        )
        html = self._render(data)
        self.assertEqual(html.count(("Lote: %s" % long_lot).encode()), 9)
        self.assertIn(b"text-overflow:ellipsis", html)
        _action, pages = self._print(self._receipt_wizard(picking, self.big_size))
        self.assertEqual(pages, 2, "el lote largo no añade páginas")

    def test_an_unencodable_lot_no_longer_drops_the_graphic(self):
        """Un lote con «Ñ» ya no deja la etiqueta sin gráfico.

        Code128 no codifica la «Ñ». Cuando el gráfico era el lote, esa
        etiqueta caía a (c), sin código que escanear. Ahora el gráfico es el
        del producto y el lote va en texto: la etiqueta sale completa.
        """
        cable = self._tracked("Cable por lotes", "CAB-LOT", "7701234500243", "lot")
        picking = self._receipt([(cable, [("LOT-Ñ-01", 2)])])
        data = self._as_sent_by_the_browser(
            self._receipt_wizard(picking).process()["data"]
        )
        values = self.report._get_report_values([], data)
        self.assertFalse(values["kt_unencodable"])
        html = self._render(data)
        self.assertEqual(self._labels_by_code(html)("7701234500243"), 2)
        self.assertEqual(html.count("Lote: LOT-Ñ-01".encode()), 2)

    def test_a_lot_on_an_untracked_product_gets_the_neutral_prefix(self):
        """Sin seguimiento pero con lote: «Lote/S/N:», que no afirma nada.

        Pasa si alguien cambia el seguimiento del producto después de
        recibir. No se sabe si era un lote o un serial, así que el prefijo
        no elige. Aquí los datos se pasan directos: stock solo genera este
        caso con un producto que cambió después.
        """
        loose = self._product("Tuerca suelta", "TUE-SUE", "7701234500250")
        loose = loose.product_variant_id
        self.assertEqual(loose.tracking, "none")
        data = self._as_sent_by_the_browser(
            {
                "active_model": "product.product",
                "quantity_by_product": {},
                "custom_barcodes": {loose.id: [("X-77", 1)]},
                "kt_label_size_id": self.size.id,
            }
        )
        html = self._render(data)
        self.assertEqual(html.count(b"Lote/S/N: X-77"), 1)
        self.assertEqual(self._labels_by_code(html)("7701234500250"), 1)

    # --- texto del PDF real ---------------------------------------------------

    def test_the_pdf_text_keeps_accents_and_enye(self):
        """El TEXTO del PDF lleva tildes y Ñ tal cual, no «Ã³» ni «Ã‘».

        Las demás pruebas miran el HTML, que ya sale bien: el fallo estaba
        después, en el PDF (LA-111). Sin `div.article`, `_prepare_html` de
        Odoo 19 pasa los hijos de `<main>` sin `web.minimal_layout` y, por
        tanto, sin `<meta charset>`; `_run_wkhtmltopdf` escribe el body en
        UTF-8 y wkhtmltopdf lo leía como Latin-1. Se genera el PDF con el
        binario real, por el camino de la recepción, y se lee su texto.
        """
        pegante = self._tracked(
            "Pegante epóxico bicomponente", "PEG-EPO-BI", "7701234500267", "lot"
        )
        cano = self._product(
            'Caño galvanizado 1/2" x 6 m', "CAN-GAL-12", "7701234500274"
        )
        cano = cano.product_variant_id
        picking = self._receipt([(pegante, [("L-ÑAN-01", 2)]), (cano, [(False, 1)])])
        action = self._receipt_wizard(picking).process()
        pdf_bytes, content_type = (
            self.env["ir.actions.report"]
            .with_context(force_report_rendering=True)
            ._render_qweb_pdf(
                action["report_name"],
                data=self._as_sent_by_the_browser(action["data"]),
            )
        )
        self.assertEqual(content_type, "pdf")
        reader = PdfFileReader(io.BytesIO(pdf_bytes), strict=False)
        text = " ".join(
            " ".join((page.extract_text() or "").split()) for page in reader.pages
        )
        self.assertNotIn(
            "Ã", text, "el texto del PDF sale como Latin-1: %r" % text[:300]
        )
        self.assertIn("Pegante epóxico bicomponente", text)
        self.assertIn('Caño galvanizado 1/2" x 6 m', text)
        self.assertEqual(text.count("Lote: L-ÑAN-01"), 2)
