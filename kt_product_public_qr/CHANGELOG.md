# Changelog — kt_product_public_qr

## 19.0.2.0.0 (2026-08-24)

- Separa la ficha QR pública neutral de la integración Professional de códigos
  alternos.
- Elimina la dependencia dura de `kt_product_multi_barcode` y publica un
  contrato de valores/puntos QWeb para extensiones de capas superiores.
- Mantiene tokens, imágenes públicas, variantes, PDF, PNG y QR base.

## 19.0.1.5.2 (15/08/2026)

* **Bug funcional real corregido (no solo de test) — el botón
  "Regenerar enlace público" no actualizaba el enlace/QR mostrado:**
  a `_compute_kt_public_qr_url` le faltaba el decorador `@api.depends
  ('kt_public_access_token', 'kt_public_website_id.domain')` — sin
  eso, Odoo no tenía forma de saber que el campo debía recomputarse
  al regenerar el token. El token SÍ cambiaba, pero `kt_public_qr_url`
  (y el QR derivado de él, `kt_public_qr_barcode_src`, que sí depende
  correctamente de `kt_public_qr_url`) quedaban con el valor viejo
  cacheado hasta que algo MÁS invalidara el campo por otra razón —
  detectado al correr el test real por primera vez contra Odoo. 100%
  verde, se suma a `MODULES_VERIFIED`.

## 19.0.1.5.1 (07/08/2026)

**Corregido — `ParseError` real al actualizar `kt_marketplace_feed_sync`:**
la ficha de variante (`product.product`) reutiliza la vista de
formulario de la plantilla — el botón «Regenerar enlace» (creado en
`product.template`) fallaba al validar la acción cuando otro módulo
(`kt_marketplace_feed_sync`) heredaba esa misma vista sobre
`product.product`. Se agregó `action_kt_regenerate_public_token` en
`product.product` (mismo patrón ya usado por
`action_open_kt_public_page`), delegando a la plantilla.

## 19.0.1.5.0 (04/08/2026)

**Reorganización arquitectónica — CONFIRMADA funcionando con una
prueba real:** la infraestructura genérica de impresión de etiquetas
(tamaños configurables, cálculo de cuadrícula, exportación PNG/ZIP)
se movió a un módulo nuevo y compartido, `kt_label_printing` — para
que `kt_product_multi_barcode` también pueda reutilizarla más
adelante, en vez de duplicarla. Este módulo ahora depende de
`kt_label_printing`. Sin cambios de comportamiento para el usuario
final — el modelo de tamaños se renombró internamente
(`kt.public.qr.label.size` → `kt.label.size`, ahora genérico), visible
en el mismo menú de antes. Ver
`disenos_completos/kt_label_printing/DISENO_ARQUITECTURA_ETIQUETAS.md`
para la razón completa de este cambio.

## 19.0.1.4.0 (04/08/2026)

**Agregado — tamaños de etiqueta configurables:** nuevo modelo
("Tamaños de etiqueta QR", en Inventario → Control de inventario) —
describe el tamaño físico real de la etiqueta y de la hoja/rollo (en
milímetros), y calcula automáticamente cuántas caben por hoja. Nueva
opción "QR público - Tamaño personalizado" en el asistente de
impresión, que usa el tamaño elegido para dibujar el QR y la celda
con las medidas exactas configuradas (antes, los 4 formatos tenían
medidas fijas escritas en el código). Trae 3 tamaños de ejemplo
precargados (A4 cuadrado, A4 pequeño, rollo térmico de 4 pulgadas).
**Código nuevo, todavía sin probar en un servidor real.**

## 19.0.1.3.0 (04/08/2026)

**Agregado — exportación masiva de PNG:** nuevo asistente
("Exportar QR como PNG (masivo)", en el menú Acción de la lista de
productos, mismo mecanismo exacto que usa Odoo para "Imprimir
etiquetas") — genera un PNG de 300x300 por cada producto
seleccionado y los empaqueta en un solo archivo ZIP para descargar.
Genera las imágenes llamando directo al método interno de Odoo
(`ir.actions.report.barcode()`), sin pasar por HTTP. **Código nuevo,
todavía sin probar en un servidor real.**

## 19.0.1.2.0 (04/08/2026)

**Agregado — formato cuadrado, recomendado:** "QR público - Cuadrado
(recomendado)", 3 columnas x 5 filas (15 etiquetas por hoja A4),
diseñado desde cero para QR — QR de 30mm (contra los 18mm de los
formatos heredados) en una celda genuinamente cuadrada de ~63x55mm.
Los 3 formatos anteriores (2x7, 4x7, 4x12) se mantienen disponibles,
marcados en la interfaz como "heredado, formato lineal" — se
reutilizaron por conveniencia de los formatos nativos de Odoo (código
de barras lineal, no pensados originalmente para QR).

**Corregido — bug real y serio, encontrado con una prueba real:**
todos los productos que ya existían antes de instalar el módulo
compartían el MISMO token de acceso público (y por lo tanto, el mismo
enlace, mostrando siempre el mismo producto sin importar cuál se
imprimiera) — Odoo, al agregar una columna nueva con valor por
defecto calculado a una tabla con registros existentes, calcula ese
valor una sola vez y lo aplica igual a todas las filas. Corregido con
un `post_init_hook` para instalaciones nuevas, y con una corrección
manual por consola para instalaciones ya existentes (ver
`docs/ESTADO.md`).

## 19.0.1.1.1 – 19.0.1.1.4 (04/08/2026)

3 bugs reales, encontrados y corregidos durante la primera instalación
real de la función de impresión masiva:
- **Colisión de IDs:** la plantilla QWeb y la acción de reporte
  usaban el mismo identificador — Odoo exige que cada uno sea único,
  sin importar el modelo.
- **`page_numbers` llegaba vacío:** el nombre de la clase Python que
  prepara los datos del reporte debe coincidir EXACTAMENTE con el
  campo `report_name` de la acción — al acortar uno sin el otro, Odoo
  dejaba de encontrar la clase y usaba un modo genérico sin los datos
  necesarios.
- **"Table name ... is too long":** el nombre completo del modelo
  (módulo + reporte) superaba el límite de 63 caracteres de
  PostgreSQL para nombres de tabla — acortado.

## 19.0.1.1.0 (04/08/2026)

**Agregado — impresión masiva en cuadrícula:** 3 formatos nuevos
(2x7, 4x7, 4x12) agregados al asistente nativo de etiquetas de Odoo
(`product.label.layout`) — permite imprimir el QR público de varios
productos a la vez, organizados en una sola hoja, en vez de una
página de PDF por producto. **Código nuevo, todavía sin probar en un
servidor real** — ver `docs/DISENO_IMPRESION_MASIVA.md` para el
diseño completo y el estado de las otras 3 mejoras relacionadas
(ZPL, PNG masivo, tamaños configurables), todavía sin construir.

## 19.0.1.0.7 (03-04/08/2026)

**Corregido — QR en blanco dentro del PDF de la etiqueta:** la
imagen del código QR se veía bien en la página web pública, pero
aparecía vacía dentro del PDF de la etiqueta — el motor que genera el
PDF no resuelve rutas relativas de la misma forma que un navegador
navegando la página en vivo. Corregido usando la URL absoluta
(con dominio completo) en vez de una ruta relativa.

## 19.0.1.0.6 (04/08/2026)

**Corregido — QR aplastado, prácticamente ilegible:** los valores por
defecto del generador nativo de códigos de barras de Odoo son
`width=600, height=100` — pensados para un código de barras lineal
(ancho y bajo), nunca para un QR (que debe ser cuadrado). Corregido
pasando explícitamente `width=300&height=300`.

## 19.0.1.0.5 (03/08/2026)

**Corregido — QR con caracteres corruptos:** al escanear el QR con
un lector, mostraba texto corrupto (`httpsÑ--dominio.com-...` en vez
de la URL real) — los caracteres especiales de la URL (`:`, `/`)
nunca se codificaban correctamente antes de insertarse en la imagen.
Corregido con `urllib.parse.quote` antes de construir la ruta de la
imagen, usando el patrón oficial documentado en el propio código
fuente de Odoo (`/report/barcode/...`).

## 19.0.1.0.4 (04/08/2026)

**Corregido — error real al abrir la página pública desde una
variante específica:** `AttributeError: The method
'product.product.action_open_kt_public_page' does not exist` — el
botón "Página pública" también aparece en la ficha de una variante
(`product.product`), pero el método solo existía en la plantilla
(`product.template`). Se agregó el mismo método en `product.product`,
delegando a la plantilla.

## 19.0.1.0.3 (03/08/2026)

**Agregado — soporte de variantes:** un producto con varias
variantes ahora muestra una sección por cada una, con su propio
código de barras oficial (el real, de la variante — el de plantilla
queda vacío cuando hay varias) y sus propios códigos alternos,
claramente separados. Antes se mostraban todos los códigos alternos
revueltos, sin indicar a cuál variante pertenecía cada uno.

## 19.0.1.0.2 (03/08/2026)

**Corregido — la imagen del producto no se veía sin sesión
iniciada:** la ruta genérica de Odoo para imágenes (`/web/image/...`)
hace su propia revisión de permisos, independiente de que el
controlador principal ya use `sudo()` — para un producto no publicado
en la tienda en línea, un visitante anónimo no tenía permiso de
lectura normal. Se agregó una ruta de imagen propia
(`/producto/<token>/imagen`), con su propio `sudo()`.

## 19.0.1.0.1 (03/08/2026)

**Resuelto — bloqueo real de 3 días:** el modelo de sitios web de
Odoo se llama `website`, no `website.website` como se había asumido
el 31/07/2026 sin verificar contra el código fuente — nunca fue un
problema del servidor. Corregido el campo `kt_public_website_id`.

## 19.0.1.0.0

Primera versión — nunca instalada en un servidor real debido al
bloqueo resuelto en 19.0.1.0.1. Página pública sin login, token único
por producto, soporte de multi-sitio web, etiqueta QR imprimible.
