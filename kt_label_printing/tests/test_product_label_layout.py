# -*- coding: utf-8 -*-
"""Pruebas del asistente de etiquetas: la opción propia y su aviso.

Lo que se comprueba no es la maquetación, sino que **el recuento llega a la
pantalla y nombra a los productos**, y que llega **solo** con la opción que
aplica ese respaldo: el valor de este aviso está en que quien imprime se
entere antes, no en cómo se ve.
"""

from unittest.mock import patch

from odoo.addons.kt_label_printing.report.kt_label_grid_report import KT_PRINT_FORMAT
from odoo.tests.common import TransactionCase, tagged

REPORT_MODEL = "report.kt_label_printing.report_kt_label_grid_document"


@tagged("post_install", "-at_install")
class TestProductLabelLayoutWarning(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.size = cls.env["kt.label.size"].create(
            {
                "name": "Prueba aviso",
                "label_width_mm": 48.0,
                "label_height_mm": 25.0,
                "content_size_mm": 18.0,
                "page_width_mm": 210.0,
                "page_height_mm": 297.0,
                "margin_mm": 5.0,
            }
        )

    def _product(self, name, code=None, barcode=None):
        return self.env["product.template"].create(
            {"name": name, "default_code": code, "barcode": barcode}
        )

    def _wizard(self, products, print_format=KT_PRINT_FORMAT):
        values = {
            "print_format": print_format,
            "custom_quantity": 1,
            "product_tmpl_ids": [(6, 0, products.ids)],
        }
        if print_format == KT_PRINT_FORMAT:
            values["kt_label_size_id"] = self.size.id
        return self.env["product.label.layout"].create(values)

    def test_no_warning_when_every_product_has_its_own_barcode(self):
        """Si no hay nada que decir, el asistente no cambia de aspecto."""
        products = self._product("A", "A-1", "7700000000512") + self._product(
            "B", "B-1", "7700000000529"
        )
        self.assertFalse(self._wizard(products).kt_label_code_warning)

    def test_the_warning_counts_and_names_the_sku_fallbacks(self):
        con = self._product("Con EAN", "C-2", "7700000000536")
        sku = self._product("Tornillo suelto 1/2", "FER-TOR-0012", False)
        warning = self._wizard(con + sku).kt_label_code_warning
        self.assertIn("1 con el SKU", warning)
        self.assertIn("FER-TOR-0012", warning)
        self.assertNotIn("C-2", warning, "el que lleva su código no se nombra")

    def test_the_warning_separates_no_code_from_unprintable_code(self):
        """Son dos cosas distintas y se cuentan aparte.

        «No hay código» es un hecho del catálogo; «hay uno y no se puede
        imprimir» es un dato que alguien debería corregir.
        """
        # Sin referencia Y sin código de barras: sólo así cae en (c) por no
        # tener ninguno. Con referencia caería en (b), que es otra cosa.
        nada = self._product("Cable a medida", False, False)
        raro = self._product("Tornillo especial", "TORNILLO-Ñ", False)
        warning = self._wizard(nada + raro).kt_label_code_warning
        self.assertIn("sin código de barras impreso", warning)
        self.assertIn("Cable a medida (sin ningún código)", warning)
        self.assertIn("TORNILLO-Ñ (su código no se puede imprimir)", warning)
        self.assertNotIn("con el SKU", warning, "ninguno de los dos va por (b)")

    def test_names_and_codes_are_escaped_in_the_warning(self):
        """Un nombre con «&» y «<» aparece escapado, no como HTML.

        Nombres y referencias los escribe quien da de alta el producto: el
        aviso los muestra tal cual se escribieron, y nunca como marcado.
        """
        nada = self._product("Tornillo <M6> & tuerca", False, False)
        # ASCII: Code128 lo codifica, así que sale por el SKU.
        sku = self._product("Pieza rara", "A&B<C>", False)
        warning = str(self._wizard(nada + sku).kt_label_code_warning)
        self.assertIn("Tornillo &lt;M6&gt; &amp; tuerca (sin ningún código)", warning)
        self.assertIn("fabricante): A&amp;B&lt;C&gt;</p>", warning)
        self.assertNotIn("<M6>", warning)
        self.assertNotIn("<C>", warning)

    def test_a_standard_format_neither_computes_nor_shows_the_warning(self):
        """Con un formato estándar no se clasifica nada y no hay aviso.

        Esos formatos imprimen el informe nativo, que no aplica el respaldo
        por SKU: avisar de él sería falso, y clasificar generaría una imagen
        de código de barras por producto para nada. La misma tanda, con la
        opción propia, sí avisa: la diferencia la hace el formato.
        """
        sku = self._product("Tornillo suelto 5/8", "FER-TOR-0058", False)
        nada = self._product("Cable a medida", False, False)
        products = sku + nada
        report_class = type(self.env[REPORT_MODEL])
        original = report_class._kt_printable_label_code
        calls = []

        def counting(report, product, images=None):
            calls.append(product.id)
            return original(report, product, images)

        with patch.object(report_class, "_kt_printable_label_code", counting):
            standard = self._wizard(products, print_format="4x12")
            self.assertFalse(standard.kt_label_code_warning)
            self.assertEqual(calls, [], "con 4x12 no se clasifica ningún producto")

            own = self._wizard(products)
            self.assertIn("FER-TOR-0058", own.kt_label_code_warning)
            self.assertEqual(len(calls), 2, "con la opción propia, uno por producto")

        view = self.env.ref(
            "kt_label_printing.product_label_layout_form_kt_label_printing"
        )
        self.assertIn(
            "print_format != '%s' or not kt_label_code_warning" % KT_PRINT_FORMAT,
            view.arch,
            "la vista oculta el aviso fuera de la opción propia",
        )

    def test_the_size_field_belongs_to_the_own_option(self):
        """El tamaño se ve y se exige solo con la rejilla PDF Kuvexta."""
        view = self.env.ref(
            "kt_label_printing.product_label_layout_form_kt_label_printing"
        )
        self.assertEqual(view.model, "product.label.layout")
        self.assertIn("kt_label_code_warning", view.arch)
        self.assertIn("invisible=\"print_format != '%s'\"" % KT_PRINT_FORMAT, view.arch)
        self.assertIn("required=\"print_format == '%s'\"" % KT_PRINT_FORMAT, view.arch)
