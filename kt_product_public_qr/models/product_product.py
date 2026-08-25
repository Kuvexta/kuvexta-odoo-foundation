# -*- coding: utf-8 -*-
from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def action_open_kt_public_page(self):
        """Corrección real (04/08/2026): el botón "Página pública"
        también aparece en la ficha de una VARIANTE específica
        (`product.product`), no solo en la de la plantilla — porque
        la vista de una variante reutiliza/extiende la misma
        estructura de formulario. El método original solo existía en
        `product.template`, causando:
        `AttributeError: The method 'product.product.action_open_kt_public_page'
        does not exist` al hacer clic desde una variante.

        La página pública es una sola por PLANTILLA (un solo QR
        agrupador muestra todas las variantes juntas, con sus propios
        códigos cada una — ver `views/product_public_info_templates.xml`)
        — así que aquí simplemente se delega a la plantilla, no se
        duplica ningún token ni URL por variante."""
        self.ensure_one()
        return self.product_tmpl_id.action_open_kt_public_page()

    def action_kt_regenerate_public_token(self):
        """La ficha de variante reutiliza la vista de plantilla; el botón
        «Regenerar enlace» debe existir también en ``product.product``
        (mismo patrón que ``action_open_kt_public_page``). Sin esto,
        al heredar ``product.product`` form (p.ej. feed ML) Odoo valida
        la acción y falla el upgrade.
        """
        return self.mapped("product_tmpl_id").action_kt_regenerate_public_token()
