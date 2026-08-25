# -*- coding: utf-8 -*-
import uuid
from urllib.parse import quote

from odoo import _, api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    kt_public_access_token = fields.Char(
        string="Token de acceso público",
        copy=False,
        index=True,
        default=lambda self: uuid.uuid4().hex,
        help="Token aleatorio usado en el enlace público del producto "
        "(página que abre el QR agrupador, sin necesidad de sesión "
        "de Odoo). No editar manualmente.",
    )
    kt_public_qr_url = fields.Char(
        string="Enlace público del producto",
        compute="_compute_kt_public_qr_url",
        help="Página pública (sin login) con información básica del "
        "producto y su código oficial por variante. No "
        "muestra proveedor, canal, ni cantidad en stock.",
    )
    kt_public_qr_barcode_src = fields.Char(
        string="Ruta de imagen del QR (uso interno del reporte)",
        compute="_compute_kt_public_qr_barcode_src",
        help="Corrección real (04/08/2026): al insertar la URL pública "
        "directamente en la etiqueta, sin codificar sus caracteres "
        'especiales (":", "/"), el QR resultante quedaba corrupto '
        "— confirmado escaneándolo con un lector real, leía "
        '"httpsÑ--dominio.com-producto-..." en vez de la URL '
        "real. Este campo aplica el escapado correcto "
        "(`urllib.parse.quote`) antes de construir la ruta de la "
        "imagen (`/report/barcode/QR/<url codificada>`), el "
        "patrón documentado en el propio código fuente de Odoo "
        "(`addons/web/controllers/report.py`).",
    )
    kt_public_website_id = fields.Many2one(
        "website",
        string="Sitio web de la página pública",
        help="Solo necesario cuando varios dominios comparten la misma "
        "base de datos (ej. varias marcas/negocios en una sola "
        "instancia). Si se deja vacío, se usa el dominio genérico "
        "de la instancia.",
    )

    @api.constrains("kt_public_access_token")
    def _check_public_token_unique(self):
        for tmpl in self:
            if not tmpl.kt_public_access_token:
                continue
            duplicate = self.sudo().search(
                [
                    ("kt_public_access_token", "=", tmpl.kt_public_access_token),
                    ("id", "!=", tmpl.id),
                ],
                limit=1,
            )
            if duplicate:
                # Colisión astronómicamente improbable con uuid4, pero se
                # regenera automáticamente en vez de bloquear al usuario.
                tmpl.kt_public_access_token = uuid.uuid4().hex

    @api.depends("kt_public_access_token", "kt_public_website_id.domain")
    def _compute_kt_public_qr_url(self):
        # Bug real (15/08/2026, CHECKLIST_MODULOS_ODOO.md §37): sin
        # este `@api.depends`, Odoo no tiene forma de saber que este
        # campo necesita recomputarse cuando cambia `kt_public_access_
        # token` — el botón "Regenerar enlace público" cambiaba el
        # token de verdad, pero el ENLACE/QR mostrado quedaba con el
        # valor viejo cacheado hasta que algo MÁS invalidara el campo
        # por otra razón. `_compute_kt_public_qr_barcode_src` (abajo)
        # sí depende de `kt_public_qr_url` — con este fix, la cadena
        # completa se recomputa correctamente.
        default_base_url = (
            self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        )
        for tmpl in self:
            if tmpl.kt_public_access_token and isinstance(tmpl.id, int):
                base_url = tmpl.kt_public_website_id.domain or default_base_url
                tmpl.kt_public_qr_url = (
                    f"{base_url}/producto/{tmpl.kt_public_access_token}"
                )
            else:
                tmpl.kt_public_qr_url = False

    @api.depends("kt_public_qr_url")
    def _compute_kt_public_qr_barcode_src(self):
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        for tmpl in self:
            if tmpl.kt_public_qr_url:
                # safe='' escapa TODO, incluidos ':' y '/' — necesario
                # porque la ruta del reporte de códigos de barras
                # (`/report/barcode/QR/<path:value>`) solo permite '/'
                # de forma segura dentro del propio mecanismo de rutas
                # de Werkzeug, pero no garantiza el resto de
                # caracteres especiales de una URL completa.
                encoded_url = quote(tmpl.kt_public_qr_url, safe="")
                # IMPORTANTE (corrección real, 04/08/2026): los
                # valores por defecto de `ir.actions.report.barcode()`
                # son `width=600, height=100` — pensados para un
                # código de barras LINEAL (ancho y bajo), nunca para
                # un QR (que debe ser cuadrado). Sin especificar
                # ancho/alto explícitos, el QR se generaba aplastado
                # y prácticamente imposible de escanear (confirmado
                # con una prueba real: la imagen sí se generaba, pero
                # con dimensiones 600x100, no un cuadrado). Por eso
                # aquí se usa la variante de la ruta con parámetros de
                # consulta (`?barcode_type=...&value=...&width=...`),
                # pasando explícitamente 300x300 — la otra forma
                # documentada en el propio código fuente de Odoo
                # (`addons/web/controllers/report.py`).
                #
                # También (corrección real, 04/08/2026): la imagen se
                # veía bien en la página web pública, pero aparecía en
                # blanco dentro del PDF de la etiqueta — el motor que
                # convierte el reporte a PDF no es un navegador normal
                # navegando la página en vivo, y no resuelve rutas
                # RELATIVAS de la misma forma. Se usa la URL completa
                # (con dominio) en vez de una ruta relativa, para que
                # pueda encontrar la imagen sin importar el contexto
                # desde el que se genere el PDF.
                tmpl.kt_public_qr_barcode_src = (
                    f"{base_url}/report/barcode/?barcode_type=QR"
                    f"&value={encoded_url}&width=300&height=300"
                )
            else:
                tmpl.kt_public_qr_barcode_src = False

    def action_kt_regenerate_public_token(self):
        """Botón 'Regenerar enlace público' — antes solo se podía hacer
        por shell (ver docs/FAQ.md). Invalida el enlace/QR público
        ANTERIOR de inmediato (deja de resolver el producto — ver
        `controllers/main.py`, que busca por `kt_public_access_token`
        exacto) y genera uno nuevo. Útil si el enlace se compartió o
        filtró por error. La etiqueta QR ya impresa con el token
        anterior debe reimprimirse; no hay forma de "avisar" a quien
        ya tenga el QR viejo impreso."""
        for tmpl in self:
            tmpl.kt_public_access_token = uuid.uuid4().hex
        if len(self) == 1:
            message = _(
                "Se regeneró el enlace público de '%(product)s'. El "
                "enlace/QR anterior YA NO FUNCIONA — reimprima la "
                "etiqueta si la tenía en uso.",
                product=self[0].display_name,
            )
        else:
            message = _(
                "Se regeneraron %(count)s enlaces públicos. Los "
                "enlaces/QR anteriores YA NO FUNCIONAN — reimprima las "
                "etiquetas si las tenía en uso.",
                count=len(self),
            )
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Enlace público regenerado"),
                "message": message,
                "sticky": True,
                "type": "warning",
            },
        }

    def action_open_kt_public_page(self):
        """Abre la página pública del producto en una pestaña nueva,
        para verificar cómo se ve antes de imprimir la etiqueta QR."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": self.kt_public_qr_url,
            "target": "new",
        }

    def _kt_public_qr_page_values(self, website):
        """Contrato neutral para extender la ficha sin acoplar Foundation.

        Los módulos de capas superiores pueden agregar valores y heredar la
        plantilla, pero la base nunca importa ni consulta sus modelos.
        """
        self.ensure_one()
        single_variant = (
            self.product_variant_ids[0]
            if len(self.product_variant_ids) == 1
            else self.env["product.product"]
        )
        return {
            "product": self,
            "single_variant": single_variant,
            "kt_public_qr_website": website,
        }

    def action_open_kt_png_export_wizard(self):
        """Abre el asistente de exportación masiva de PNG — mismo
        patrón exacto que usa Odoo para el asistente nativo de
        etiquetas (`product.template.action_open_label_layout`,
        verificado contra el código fuente real): un método que
        resuelve la acción y le pasa los productos ya seleccionados
        como contexto por defecto."""
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "kt_product_public_qr.action_open_kt_png_export_wizard"
        )
        action["context"] = {"default_product_tmpl_ids": self.ids}
        return action
