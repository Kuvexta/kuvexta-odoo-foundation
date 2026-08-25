# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class ProductPublicInfoController(http.Controller):

    @http.route(
        "/producto/<string:access_token>",
        type="http",
        auth="public",
        website=True,
        sitemap=False,
    )
    def product_public_info(self, access_token, **kwargs):
        """Página pública (sin sesión de Odoo) con información básica
        del producto y su código oficial por variante.
        Deliberadamente NO expone proveedor, canal, ni cantidad
        en stock — decisión de negocio confirmada el 31/07/2026."""
        product = (
            request.env["product.template"]
            .sudo()
            .search([("kt_public_access_token", "=", access_token)], limit=1)
        )
        if not product:
            return request.not_found()

        # Si el producto está asignado a un sitio web específico (caso:
        # varios dominios compartiendo la misma base de datos) y la
        # petición llegó por un dominio distinto, redirige al dominio
        # correcto en vez de mostrarlo indistintamente en cualquiera.
        assigned_website = product.kt_public_website_id
        current_website = request.website
        if assigned_website and current_website and assigned_website != current_website:
            correct_url = f"{assigned_website.domain}/producto/{access_token}"
            return request.redirect(correct_url, code=302, local=False)

        return request.render(
            "kt_product_public_qr.product_public_info_page",
            product._kt_public_qr_page_values(current_website),
        )

    @http.route(
        "/producto/<string:access_token>/imagen",
        type="http",
        auth="public",
        website=True,
        sitemap=False,
    )
    def product_public_image(self, access_token, **kwargs):
        """Ruta propia para servir la imagen del producto — corrección
        real (03/08/2026): la ruta genérica de Odoo (`/web/image/...`)
        hace su PROPIA revisión de permisos de acceso, independiente
        de que el controlador principal ya use `sudo()` — para un
        producto que no está publicado en la tienda en línea
        (`website_sale`), un visitante anónimo no tiene permiso de
        lectura normal sobre `product.template`, así que esa ruta
        genérica fallaba en silencio (la página cargaba, pero sin
        imagen). Confirmado con una prueba real: con sesión iniciada
        sí se veía, sin sesión no — la diferencia exacta era el
        permiso de esa ruta específica.

        Esta ruta, en cambio, es 100% nuestra — decide ella misma
        (con `sudo()`, igual que el resto de este controlador) qué
        exponer, sin depender del permiso de lectura genérico de
        `product.template`. Usa `_get_image_stream_from`, el método
        oficial de Odoo para esto (con soporte de caché/ETag
        incluido), verificado contra el código fuente real
        (`odoo/addons/base/models/ir_binary.py`)."""
        product = (
            request.env["product.template"]
            .sudo()
            .search([("kt_public_access_token", "=", access_token)], limit=1)
        )
        if not product:
            return request.not_found()
        return (
            request.env["ir.binary"]
            ._get_image_stream_from(
                product,
                field_name="image_1920",
            )
            .get_response()
        )
