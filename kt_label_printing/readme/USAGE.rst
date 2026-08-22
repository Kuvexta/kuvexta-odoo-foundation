Este módulo **no imprime nada por sí solo** — se usa desde el código
de otro módulo (hoy: ``kt_product_public_qr``), nunca directamente
desde un menú propio::

    from odoo.addons.kt_label_printing.models.kt_label_grid_utils import (
        build_label_list,
        compute_page_numbers,
    )

``build_label_list`` arma la lista de etiquetas a imprimir a partir de
un tamaño (``kt.label.size``) y el contenido a repetir; ``compute_page_
numbers`` calcula la paginación resultante. El mixin ``kt.label.png.
export.mixin`` se hereda desde el asistente de exportación masiva que
lo necesite — solo hay que generar los bytes de cada imagen, el mixin
resuelve empaquetarlos en un ZIP y armar la descarga.

Guía completa, con ejemplo real de cómo crear un tamaño de etiqueta
propio: ``MANUAL_ES.md`` (raíz de este módulo).
