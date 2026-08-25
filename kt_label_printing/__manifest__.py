# -*- coding: utf-8 -*-
# Copyright 2026 Kuvexta
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
{
    "name": "KT Label Printing",
    "version": "19.0.1.0.2",
    "category": "Inventory/Inventory",
    "summary": "Infraestructura genérica y reutilizable para imprimir "
    "etiquetas de producto: tamaños configurables, cálculo de "
    "cuadrícula, y exportación masiva de imágenes",
    "author": "Kuvexta",
    "maintainers": ["Kuvexta"],
    "website": "https://github.com/Kuvexta/kuvexta-odoo-foundation",
    "license": "LGPL-3",
    "development_status": "Beta",
    "depends": [
        "product",
        # 'stock' es necesario por el menu de views/kt_label_size_views.xml
        # (parent="stock.menu_stock_inventory_control") - sin esta
        # dependencia explicita, instalar este modulo junto con otro que
        # NO garantice que 'stock' ya se cargo antes falla con
        # 'External ID not found: stock.menu_stock_inventory_control'
        # (bug real encontrado el 05/08/2026 al instalar de punta a punta
        # junto con kt_qr_webkul_print, que no depende de 'stock').
        "stock",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/kt_label_size_data.xml",
        "views/kt_label_size_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
