# Copyright 2026 Kuvexta
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
{
    "name": "KT Camera Scan - Website Base",
    "version": "19.0.1.0.0",
    "category": "Website/Website",
    "summary": "Resuelve códigos oficiales a productos públicos desde la cámara",
    "author": "Kuvexta",
    "maintainers": ["Kuvexta"],
    "website": "https://github.com/Kuvexta/kuvexta-odoo-foundation",
    "license": "LGPL-3",
    "development_status": "Beta",
    "depends": ["website_sale", "kt_camera_scan_widget"],
    "data": ["views/website_camera_scan_templates.xml"],
    "assets": {
        "web.assets_frontend": [
            "kt_camera_scan_widget/static/src/js/camera_scan_service.js",
            "kt_camera_scan_website_base/static/src/css/website_camera_scan.css",
            "kt_camera_scan_website_base/static/src/js/website_camera_scan.js",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
