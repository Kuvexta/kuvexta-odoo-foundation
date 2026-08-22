# -*- coding: utf-8 -*-
import base64
import io
import re
import zipfile

from odoo import models


class KtLabelPngExportMixin(models.AbstractModel):
    _name = "kt.label.png.export.mixin"
    _description = "Mixin genérico: empaqueta varias imágenes en un ZIP"

    @staticmethod
    def _kt_safe_filename(name):
        """Limpia un nombre para usarlo como nombre de archivo — quita
        caracteres que no son válidos en un nombre de archivo en
        ningún sistema operativo común."""
        safe = re.sub(r'[\\/*?:"<>|]', "", name or "").strip()
        return safe or "archivo"

    def _kt_build_zip_download_action(self, files, zip_filename="imagenes.zip"):
        """Recibe una lista de `(nombre_base, bytes_de_la_imagen)` —
        SIN necesitar saber qué tipo de imagen es, ni de dónde salió
        cada una (código de barras, QR, cualquier otra cosa) — arma
        un único ZIP y retorna la acción de descarga lista para usar.

        Reutilizable por cualquier módulo que necesite exportar varias
        imágenes de golpe: cada uno solo necesita generar sus propios
        bytes de imagen (con el método que le corresponda) y llamar a
        este mixin para la parte que sí es igual siempre — evitar
        nombres repetidos dentro del ZIP, y empaquetar/descargar."""
        buffer = io.BytesIO()
        used_names = {}
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for base_name, image_bytes in files:
                safe_name = self._kt_safe_filename(base_name)
                count = used_names.get(safe_name, 0)
                used_names[safe_name] = count + 1
                suffix = f"-{count + 1}" if count else ""
                zf.writestr(f"{safe_name}{suffix}.png", image_bytes)

        attachment = self.env["ir.attachment"].create(
            {
                "name": zip_filename,
                "type": "binary",
                "datas": base64.b64encode(buffer.getvalue()),
                "res_model": self._name,
                "res_id": self.id if isinstance(self.id, int) else 0,
            }
        )
        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/{attachment.id}?download=true",
            "target": "self",
        }
