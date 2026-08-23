# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    kt_camera_scan_enabled = fields.Boolean(
        related="company_id.kt_camera_scan_enabled",
        readonly=False,
        string="Habilitar escaneo por cámara",
    )
    kt_camera_scan_beep_enabled = fields.Boolean(
        related="company_id.kt_camera_scan_beep_enabled",
        readonly=False,
        string="Sonido de confirmación al escanear",
    )
    kt_camera_scan_default_facing = fields.Selection(
        related="company_id.kt_camera_scan_default_facing",
        readonly=False,
        string="Cámara por defecto",
    )
