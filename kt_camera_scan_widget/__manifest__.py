# -*- coding: utf-8 -*-
# Copyright 2026 Kuvexta
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
{
    "name": "KT Camera Scan Widget",
    "version": "19.0.1.2.0",
    "category": "Technical Settings",
    "summary": "Motor reutilizable de escaneo por cámara (código de "
    "barras/QR) — backend, POS y website vía módulos puente; "
    "sin lógica de negocio propia",
    "author": "Kuvexta",
    "maintainers": ["Kuvexta"],
    "website": "https://github.com/Kuvexta/odoo-community-tools",
    "license": "LGPL-3",
    "development_status": "Alpha",
    "depends": ["web"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_config_settings_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "kt_camera_scan_widget/static/src/js/camera_scan_service.js",
            "kt_camera_scan_widget/static/src/js/camera_scan_widget.js",
            "kt_camera_scan_widget/static/src/xml/camera_scan_widget.xml",
            "kt_camera_scan_widget/static/src/scss/camera_scan_widget.scss",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
