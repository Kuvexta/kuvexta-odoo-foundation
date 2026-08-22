Infraestructura **genérica y reutilizable** para imprimir etiquetas
de producto — sin ninguna opinión sobre QUÉ se dibuja en cada
etiqueta (código de barras, QR, o cualquier otra cosa). Otros módulos
(hoy: ``kt_product_public_qr``) construyen su propio contenido de
etiqueta apoyándose en este módulo para las partes que siempre son
iguales: calcular cuántas etiquetas caben por hoja, administrar
tamaños configurables según el rollo/papel físico, y empaquetar
varias imágenes en un ZIP descargable.

**Por qué existe este módulo separado:** ver
``disenos_completos/kt_label_printing/DISENO_ARQUITECTURA_ETIQUETAS.md``
— resumen corto: esta infraestructura no tiene nada de específico a
ningún módulo en particular, y más de uno la necesita (o la va a
necesitar). ``kt_product_multi_barcode`` todavía no migró a este
módulo — sigue usando el asistente nativo de Odoo tal cual (ver
``PENDIENTES.md``).

**Guía en español, con ejemplo de cómo crear un tamaño de etiqueta
propio:** ``MANUAL_ES.md`` (raíz de este módulo).

Provee:

- **Modelo** ``kt.label.size`` — describe el tamaño físico real de una
  etiqueta y de la hoja/rollo donde se imprime (en milímetros), y
  calcula automáticamente cuántas etiquetas caben por hoja.
  Administrable desde ``Inventario → Control de inventario →
  Tamaños de etiqueta``.
- ``kt_label_grid_utils.py`` — funciones puras de Python
  (``build_label_list``, ``compute_page_numbers``) para armar la
  lista de etiquetas a imprimir y calcular la paginación —
  reutilizables desde cualquier reporte QWeb propio.
- **Mixin** ``kt.label.png.export.mixin`` — para que cualquier
  asistente de exportación masiva de imágenes solo tenga que generar
  sus propios bytes de imagen; el mixin resuelve empaquetarlas en un
  ZIP y armar la descarga.

Este módulo **no imprime nada por sí solo** — no tiene sentido
instalarlo sin al menos otro módulo que lo use (hoy:
``kt_product_public_qr``).
