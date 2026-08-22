# -*- coding: utf-8 -*-
# Copyright 2026 Kuvexta
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
from odoo import models


class ResCompany(models.Model):
    _inherit = "res.company"

    def _kt_resolve_toggle(self, key, warehouse=None):
        """Devuelve el valor efectivo de un interruptor de
        ``kt_advanced_stock_flows`` para ``self`` (la compañía),
        respetando primero cualquier excepción registrada para
        ``warehouse`` — si no hay excepción (o no se pasó bodega),
        cae al valor normal de la compañía, exactamente el mismo
        comportamiento que sin este módulo instalado.
        """
        self.ensure_one()
        if warehouse:
            override = self.env["kt.toggle.override"].search(
                [("warehouse_id", "=", warehouse.id), ("toggle_key", "=", key)],
                limit=1,
            )
            if override:
                return override.value
        return getattr(self, key, False)
