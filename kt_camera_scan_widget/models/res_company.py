# -*- coding: utf-8 -*-
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    kt_camera_scan_enabled = fields.Boolean(
        string="Habilitar escaneo por cámara",
        default=True,
        help="Si el escaneo por cámara está disponible donde lo "
        "soportan los módulos puente: ScanFlow (documentos), "
        "kt_camera_scan_pos (POS), kt_camera_scan_website "
        "(tienda /shop y botón flotante en la web pública). "
        "Este módulo por sí solo no agrega botones — es "
        "infraestructura reutilizable.",
    )
    kt_camera_scan_beep_enabled = fields.Boolean(
        string="Sonido de confirmación al escanear",
        default=True,
        help="Si se reproduce un sonido corto al detectar un código "
        "válido con la cámara.",
    )
    kt_camera_scan_default_facing = fields.Selection(
        [
            ("environment", "Cámara trasera (recomendado)"),
            ("user", "Cámara frontal"),
        ],
        string="Cámara por defecto",
        default="environment",
        help="Qué cámara del dispositivo se abre primero al iniciar el "
        "escaneo — el usuario puede cambiarla manualmente si el "
        "dispositivo tiene más de una.",
    )
