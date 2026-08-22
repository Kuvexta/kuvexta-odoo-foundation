# Changelog — kt_label_printing

## 19.0.1.0.2 (15/08/2026)

* Doc-only: se estandarizó `README.rst` al patrón de carpeta `readme/`
  (`DESCRIPTION.rst`, `CONFIGURE.rst`, `ROADMAP.rst`) que usa el resto
  del repositorio, en vez de un `README.rst` autocontenido. Sin
  cambios de comportamiento.

## 19.0.1.0.1 (05/08/2026)

**Corregido:** agregada la dependencia explícita de `stock` — el
menú "Tamaños de etiqueta" cuelga de
`stock.menu_stock_inventory_control` (menú nativo de Inventario), así
que instalar este módulo sin `stock` ya instalado dejaba el menú sin
un padre válido. Detectado al verificar la instalación real junto
con `kt_qr_webkul_print`.

## 19.0.1.0.0 (05/08/2026)

**Agregado:** módulo nuevo — infraestructura genérica y reutilizable
para imprimir etiquetas de producto, sin ninguna opinión sobre qué
se dibuja en cada una (código de barras, QR, o cualquier otra cosa).

- Modelo `kt.label.size`: describe el tamaño físico real de una
  etiqueta y de la hoja/rollo donde se imprime (en milímetros), y
  calcula automáticamente cuántas etiquetas caben por hoja
  (columnas × filas). 3 tamaños de ejemplo precargados (A4 cuadrado,
  A4 pequeño, rollo térmico de 4 pulgadas).
- `kt_label_grid_utils.py`: funciones puras de Python
  (`build_label_list`, `compute_page_numbers`) para armar la lista
  de etiquetas a imprimir y calcular la paginación — reutilizables
  desde cualquier reporte QWeb propio.
- Mixin `kt.label.png.export.mixin`: para que cualquier asistente de
  exportación masiva de imágenes solo tenga que generar sus propios
  bytes de imagen; el mixin resuelve empaquetarlas en un ZIP y armar
  la descarga.

Este módulo no imprime nada por sí solo — se creó junto con
`kt_product_public_qr` (primer y único consumidor por ahora) para
aislar la parte de la lógica que no tiene nada de específico a ese
módulo en particular, pensando en que futuros módulos de etiquetas
(código de barras, precios, otros) puedan reutilizarla sin duplicar
código.
