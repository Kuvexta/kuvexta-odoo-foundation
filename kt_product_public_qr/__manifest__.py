# -*- coding: utf-8 -*-
# Copyright 2026 Kuvexta
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
{
    "name": "KT Product Public QR",
    "version": "19.0.2.0.0",
    "category": "Inventory/Inventory",
    "summary": "Ficha pública neutral enlazada desde un QR imprimible",
    # NOTE: la descripción larga vive en README.rst (ensamblada a partir
    # de readme/DESCRIPTION.rst etc.) — ver docs/ESTADO.md en esta misma
    # carpeta para el historial completo de correcciones y pruebas reales
    # (confirmado funcionando de punta a punta el 04/08/2026).
    "author": "Kuvexta",
    "maintainers": ["Kuvexta"],
    "website": "https://github.com/Kuvexta/kuvexta-odoo-foundation",
    "license": "LGPL-3",
    "development_status": "Beta",
    "depends": [
        "kt_label_printing",
        "website",
        "product",
    ],
    "data": [
        "security/ir.model.access.csv",
        "report/product_public_qr_label_report.xml",
        "report/product_public_qr_grid_report.xml",
        "views/product_views.xml",
        "views/product_public_info_templates.xml",
        "views/kt_public_qr_png_export_wizard_views.xml",
        "views/product_label_layout_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "post_init_hook": "_kt_assign_unique_public_tokens",
}
