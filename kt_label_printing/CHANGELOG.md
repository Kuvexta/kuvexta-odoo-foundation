# Changelog — kt_label_printing

## 19.0.1.1.1 (24/09/2026)

> **Corrección bajo sincronización excepcional ADR-4.5** (TASK-000090),
> igual que D1/D3. Se hace aquí porque foundation no corre pruebas Odoo (D2,
> gobernanza de foundation para cambios funcionales, sigue pendiente para
> después del piloto). T-fnd la llevará a foundation conservando sus 3 capas
> propias (autoridad documental en `README.rst` y `MANUAL_ES.md`, `website`).

### Tildes y Ñ en el texto de la Rejilla PDF (O-C5-2)

**Corrige lo que se imprime.** El texto del PDF salía como Latin-1
(«epÃ³xico», «CaÃ±o», «L-Ã‘AN-01»), también al imprimir desde la interfaz y
con cualquier `wkhtmltopdf`, parcheado o no.

* **Causa:** sin `div.article`, `_prepare_html` de Odoo 19 pasa los hijos de
  `main` sin `web.minimal_layout`, es decir, sin `<meta charset>`, y
  wkhtmltopdf leía el body UTF-8 como Latin-1.
* **Arreglo:** `<meta charset="utf-8"/>` como primer elemento de
  `report_kt_label_grid`. No ocupa sitio: la geometría no cambia.
* **Prueba nueva:** `test_the_pdf_text_keeps_accents_and_enye` lee el **texto
  del PDF real** (no el HTML) y exige tildes, «Caño» y «Lote: L-ÑAN-01».
* El comentario de la plantilla explica ahora las dos consecuencias de no
  tener `div.article`: sin CSS del layout y sin charset.

## 19.0.1.1.0 (22/09/2026)

> **Cambio funcional sobre copia congelada por ADR-4, bajo sincronización
> excepcional autorizada; el destino es foundation.** Por ADR-4 la autoridad
> de este módulo es `kuvexta-odoo-foundation`. Esta versión se hace aquí
> porque foundation no corre pruebas Odoo, y se llevará allí en **una sola**
> sincronización excepcional que incluirá las dos entradas de abajo.

### Lotes y números de serie (TASK-000084)

**Cambia lo que se imprime.** La etiqueta de un producto con lote o número de
serie lleva **los dos**: el código de barras **del producto**, con el mismo
orden de siempre (código de barras, si no SKU marcado, si no sin gráfico), y
debajo, en texto, **«Lote: X»** o **«S/N: X»** según `product.tracking`.
Antes, como el nativo de Odoo, el gráfico era el código del lote.

* Producto sin seguimiento que llega con lote: **«Lote/S/N: X»**.
* **Solo texto**: sin segundo código de barras para el lote o el serial.
* Un lote largo se recorta con puntos suspensivos; la celda, de tamaño fijo,
  no deja que desborde.
* La línea de lote resta alto al código **solo en su propia etiqueta**; las
  etiquetas sin lote no cambian.
* El recuento del informe pasa a clasificar las etiquetas de lote **por
  producto**, como ya hacía el aviso del asistente: antes no coincidían.
* Una imagen por producto, no por lote.
* Un lote que Code128 no puede codificar (`Ñ`) ya no deja la etiqueta sin
  gráfico.
* `KT_CODE_LOT` queda como constante **reservada**: ya no se imprime como
  gráfico.
* Pruebas por el camino real: recepción, selector «Etiquetas de producto»,
  «cantidades de la operación» y Rejilla PDF Kuvexta, con lote 3+2, serie
  1+1 y un producto sin seguimiento: 9 etiquetas y el PDF real.

### Registro tardío: salida PDF (PR #244, TASK-000081)

La PR #244 se fusionó el 22/09/2026 **sin subir la versión ni dejar entrada
aquí**; se registra ahora. Añadió la **Rejilla PDF Kuvexta** como opción del
asistente nativo de etiquetas, con un `kt.label.size` obligatorio del que
salen columnas, filas, celda, código y la hoja del PDF; el respaldo de código
a/b/c con el SKU marcado y la guarda de codificación; el aviso en el asistente
antes de imprimir; y las pruebas del módulo. Como la versión no subió, la
copia de foundation sigue en `19.0.1.0.2` **sin** esta salida: esta versión
es la primera que las distingue.

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

---

<sub>Nombre canónico de este archivo: `kt_label_printing/CHANGELOG.md`. Alias de coordinación, en minúsculas porque el patrón de scopes no admite mayúsculas: `repo/source/file/kt_label_printing/changelog.md`.</sub>
