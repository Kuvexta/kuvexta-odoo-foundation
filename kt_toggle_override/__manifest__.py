# -*- coding: utf-8 -*-
# Copyright 2026 Kuvexta
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
{
    "name": "KT Toggle Override",
    "version": "19.0.1.0.3",
    "category": "Inventory/Inventory",
    "summary": "Excepciones por bodega a los interruptores de "
    "kt_advanced_stock_flows (ej. bodega central compartida entre "
    "varios establecimientos con una política distinta)",
    # NOTE: per convención OCA, la descripción larga vive en README.rst
    # (ensamblada a partir de readme/*.rst), no acá.
    "author": "Kuvexta",
    "maintainers": ["Kuvexta"],
    "website": "https://github.com/Kuvexta/odoo-community-tools",
    "license": "LGPL-3",
    "development_status": "Alpha",
    "depends": [
        "stock",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/kt_toggle_override_multi_company.xml",
        "views/stock_warehouse_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
