# -*- coding: utf-8 -*-
# Copyright 2026 Kuvexta
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
{
    "name": "KT Sales Channel",
    "version": "19.0.1.3.4",
    "category": "Sales/Sales",
    "summary": "Canal de venta en pedidos (manual e integrado) y reporte " "por canal",
    # Descripción larga en README.rst (convención OCA / Kuvexta).
    "author": "Kuvexta",
    "maintainers": ["Kuvexta"],
    "website": "https://github.com/Kuvexta/odoo-community-tools",
    "license": "LGPL-3",
    "development_status": "Beta",
    "depends": [
        "sale",
        "sale_management",
        "point_of_sale",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/kt_sales_channel_multi_company.xml",
        "data/kt_sales_channel_data.xml",
        "data/kt_sales_channel_type_align.xml",
        "views/kt_sales_channel_views.xml",
        "views/sale_order_views.xml",
        "views/pos_config_views.xml",
        "views/pos_order_views.xml",
        "views/kt_sales_channel_report_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
