# -*- coding: utf-8 -*-
# Copyright 2026 Kuvexta
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
{
    "name": "KT Payment Gateway Core",
    "version": "19.0.1.0.0",
    "category": "Accounting/Payment",
    "summary": "Contratos neutrales y extensibles para adaptadores de pasarelas de pago.",
    "description": """
KT Payment Gateway Core
=======================

Capa Foundation, neutral y reutilizable. Define únicamente los puntos de
extensión genéricos que permiten encadenar adaptadores de pago sobre
``sale.order``. No contiene tarifarios, comisiones, retenciones, propinas,
split tender, settlement, crons ni automatización financiera.

La licencia efectiva de este módulo es LGPL-3. Su ubicación futura en
Foundation no autoriza a relicenciar otras capas.
""",
    "author": "Kuvexta",
    "maintainers": ["Kuvexta"],
    "website": "https://github.com/Kuvexta/odoo-community-tools",
    "license": "LGPL-3",
    "development_status": "Beta",
    "depends": ["sale_management"],
    "data": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}
