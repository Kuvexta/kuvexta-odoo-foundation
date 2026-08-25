# Diseño — Impresión masiva, ZPL, PNG masivo y tamaños configurables

**⚠️ Actualización de arquitectura (04/08/2026):** la infraestructura
GENÉRICA descrita aquí (tamaños configurables, cálculo de cuadrícula,
exportación PNG/ZIP) se migró a un módulo nuevo y compartido,
`kt_label_printing` — para que `kt_product_multi_barcode` también
pueda reutilizarla el día que la necesite, en vez de reconstruir lo
mismo. Ver
`disenos_completos/kt_label_printing/DISENO_ARQUITECTURA_ETIQUETAS.md`
para la razón completa. Este documento se conserva tal cual, como
registro histórico del diseño original — el contenido de este QR
(el reporte, las plantillas de celda) sigue siendo propio de este
módulo; solo la maquinaria genérica de abajo se movió.

**Estado:**
- ✅ **Punto 1 (impresión masiva en cuadrícula)** — construido y
  confirmado funcionando con datos reales, incluida la corrección de
  un bug real (tokens duplicados en productos ya existentes).
- ✅ **Punto 3 (exportación masiva de PNG)** — construido y
  confirmado funcionando, tras la migración a `kt_label_printing`.
- ✅ **Punto 4 (tamaños configurables)** — construido y confirmado
  funcionando, tras la migración a `kt_label_printing`.
- ⏳ Punto 2 (ZPL) — diseñado, sin construir.

Este documento define el diseño técnico completo de las 4 mejoras
pedidas para la impresión de etiquetas de `kt_product_public_qr`,
verificadas contra el código fuente real de Odoo 19.

---

## El problema actual, en concreto

El reporte de hoy (`report/product_public_qr_label_report.xml`)
genera **una página de PDF completa por cada producto** (7cm x 5cm de
contenido, dentro de una página que probablemente Odoo trata como
tamaño A4 completo por defecto) — si imprimes 50 productos, obtienes
50 hojas, cada una con una sola etiqueta pequeña en una esquina,
desperdiciando el resto del papel. Además, solo genera PDF — no hay
forma de generar ZPL (para impresoras térmicas industriales) ni PNG
en lote.

---

## 1. Impresión masiva eficiente (varias etiquetas por hoja)

**✅ Construido y CONFIRMADO funcionando con una prueba real (04/08/2026, tras la migración a `kt_label_printing`).**
Implementado exactamente como se diseñó abajo: 3 formatos nuevos
(`kt_public_qr_2x7`, `kt_public_qr_4x7`, `kt_public_qr_4x12`)
agregados al asistente nativo `product.label.layout`
(`models/product_label_layout.py`), con su propio reporte en
cuadrícula (`report/product_public_qr_grid_report.py` + `.xml`) — una
celda simple por etiqueta (nombre + QR pequeño + referencia, sin la
información completa de variantes/códigos alternos que sí tiene la
etiqueta grande de un solo producto). **Todavía no se ha probado en
un servidor real** — a diferencia de todo lo demás de este módulo,
que sí se confirmó con pruebas en vivo antes de darse por bueno.

### Hallazgo clave — ya existe un mecanismo nativo que resuelve esto

`kt_product_multi_barcode` **ya reutiliza** el asistente nativo de
Odoo para esto (`product.label.layout`, confirmado en
`MEJORAS_PENDIENTES.md` de ese módulo, punto 6) — un modelo temporal
(`TransientModel`) con un campo `print_format` (Selection: "Dymo",
"2x7 con precio", "4x12", etc.) que arma automáticamente una
**cuadrícula** de N columnas x M filas por hoja, ya resuelto por
Odoo mismo, sin que hubiera que programar el acomodo en cuadrícula.

**Verificado contra el código fuente real**
(`addons/product/wizard/product_label_layout.py`): el campo
`print_format` es un `Selection` extendible — cualquier módulo puede
agregarle sus propias opciones nuevas por herencia. El método
`_prepare_report_data()` decide qué reporte usar según el formato
elegido, construyendo el nombre técnico del reporte a partir del
patrón "NxM" (ej. `product.report_product_template_label_2x7_noprice`).

### Diseño propuesto

1. **Extender el mismo asistente nativo** (`product.label.layout`),
   agregando una opción nueva a `print_format` — ej.
   `('kt_public_qr_2x7', 'QR público (2 x 7)')`,
   `('kt_public_qr_3x8', 'QR público (3 x 8)')` — cada una
   representando una cuadrícula distinta según el tamaño de etiqueta
   típico.
2. **Un reporte nuevo por cada combinación de cuadrícula**, similar
   en estructura al reporte actual de una sola etiqueta, pero
   repitiendo el bloque de etiqueta en una tabla/grid CSS de N
   columnas, iterando sobre todos los productos seleccionados —
   exactamente el mismo patrón que ya usan los reportes nativos de
   Odoo para esto (visible en
   `addons/product/report/product_label_report_views.xml` como
   referencia real de cómo Odoo arma esa cuadrícula).
3. **Sobrescribir `_prepare_report_data()`** (heredando el wizard):
   si `print_format` empieza con `kt_public_qr_`, apuntar al XML ID
   del reporte correspondiente en vez del nativo.

### Ventaja de este enfoque

Se reutiliza toda la infraestructura ya construida y probada por
Odoo (el asistente, su vista, el flujo de "seleccionar productos →
Imprimir → Etiquetas") — el usuario ve la opción nueva mezclada
naturalmente junto a las que ya conoce, sin aprender una pantalla
distinta.

---

## 2. Etiquetas ZPL (impresión térmica directa)

**Diseño ampliado el 04/08/2026** — ya no solo ZPL: ver
`DISENO_ZPL_MULTIPROTOCOLO.md` (en esta misma carpeta) para el
diseño completo, cubriendo también EPL, TSPL y DPL, con una
arquitectura de "traductores" que evita repetir la lógica de armado
de etiqueta 4 veces — la sintaxis real de cada protocolo, confirmada
contra manuales públicos, no de memoria.

---

## 3. Exportación masiva de imágenes PNG

**✅ Construido y CONFIRMADO funcionando con una prueba real (04/08/2026, tras la migración a `kt_label_printing`).**
Implementado exactamente como se diseñó abajo: nuevo asistente
(`models/kt_public_qr_png_export_wizard.py`), enganchado al menú
Acción de la lista de productos vía una acción de servidor
(`ir.actions.server` con `binding_model_id` — el mismo mecanismo
exacto que usa Odoo para su propio "Imprimir etiquetas", verificado
contra el código fuente real).

### Diseño propuesto

1. **Mismo asistente de selección de productos** (reutilizable con
   el del punto 1).
2. **Generación en Python, sin pasar por HTTP:** en vez de llamar a
   la ruta `/report/barcode/...` una vez por producto (lento,
   innecesario dar la vuelta completa por HTTP para algo que corre en
   el mismo servidor), llamar directo al método interno
   `env['ir.actions.report'].barcode('QR', valor, width=300, height=300)`
   — el mismo método que esa ruta usa por debajo, pero sin la
   sobrecarga de una petición HTTP completa por imagen.
3. **Empaquetado en un solo archivo ZIP** para la descarga — un
   navegador no puede descargar "varios archivos sueltos" de un solo
   clic, así que se arma un ZIP en memoria (`io.BytesIO` +
   `zipfile.ZipFile`, ambos de la librería estándar de Python, sin
   dependencias nuevas) con un PNG por producto, nombrado de forma
   clara (ej. `nombre_producto-token.png`).

---

## 4. Tamaños configurables según el rollo/etiqueta física

**✅ Construido y CONFIRMADO funcionando con una prueba real (04/08/2026, tras la migración a `kt_label_printing`).**
Implementado exactamente como se diseñó abajo: nuevo modelo
`kt.public.qr.label.size` (con su propio menú de administración),
calcula automáticamente cuántas etiquetas caben por hoja a partir del
tamaño de etiqueta y de hoja/rollo configurados. Nueva opción "QR
público - Tamaño personalizado" en el asistente, con una celda que
usa `t-attf-style` para dibujar el QR con el tamaño exacto elegido en
tiempo de renderizado, en vez de un tamaño fijo en la plantilla.

### Para el caso de PDF en cuadrícula (punto 1)

Reutilizar el modelo nativo **`report.paperformat`** — verificado
contra el código fuente real
(`odoo/addons/base/models/report_paperformat.py`): ya soporta
`format='custom'` con `page_width`/`page_height` en milímetros
exactos, además de márgenes configurables. El usuario podría crear
(o elegir entre varios ya preconfigurados) un formato de papel que
coincida exactamente con su hoja de etiquetas física, y asociarlo al
reporte correspondiente.

### Para el caso de ZPL / impresión térmica continua

Las impresoras térmicas normalmente no usan "páginas" — usan un
**ancho fijo** (el del rollo, ej. 4 pulgadas) y una **altura variable
por etiqueta** (cada etiqueta termina donde el propio comando ZPL
`^XZ` lo indique). Diseño propuesto: un modelo simple propio (no
necesita ser `report.paperformat`, ese modelo está pensado para
PDF/páginas) — ej. `kt.public.qr.label.size`, con campos `name`,
`width_mm`, `height_mm` — una lista corta de tamaños típicos
preconfigurados (ej. "4x6 pulgadas", "2x1 pulgadas") más la opción de
crear uno propio, seleccionable en el asistente ZPL del punto 2.

---

## Prioridad sugerida, si se construye por etapas

1. **Impresión masiva en cuadrícula (PDF)** — el mayor impacto
   inmediato (resuelve el desperdicio de papel actual), y el que más
   reutiliza infraestructura ya existente y probada.
2. **PNG masivo** — relativamente simple de construir una vez
   resuelto el punto 1 (comparte la lógica de selección de
   productos).
3. **Tamaños configurables** — depende de tener primero el punto 1
   construido, para saber exactamente qué parámetros necesita
   exponerse.
4. **ZPL** — el de mayor esfuerzo (mecanismo completamente aparte,
   sin poder reutilizar QWeb/PDF), dejarlo para cuando haya una
   necesidad real confirmada de imprimir en una impresora térmica
   específica.

## Preguntas abiertas para cuando se decida construir esto

- ¿Qué tamaños de etiqueta/rollo se usan realmente en la operación
  de Nexo Ferretero / SUBIENES? (para preconfigurar los formatos más
  usados, en vez de dejar todo en blanco desde el inicio).
- Para ZPL: ¿ya existe una impresora térmica de red disponible para
  probar el envío directo, o por ahora bastaría con la descarga del
  archivo `.zpl`?
- ¿La impresión masiva debe respetar el mismo diseño de dominio
  múltiple del módulo (usar la URL del sitio web asignado a cada
  producto, no siempre el dominio genérico)? — Sí, por consistencia
  con el resto del módulo, cada etiqueta debe usar el
  `kt_public_qr_url` ya calculado de cada producto (que ya resuelve
  esto correctamente), sin necesitar ningún cambio adicional para
  este caso.
