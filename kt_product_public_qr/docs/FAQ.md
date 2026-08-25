# Preguntas frecuentes — kt_product_public_qr

## ¿Este módulo reemplaza a `kt_product_multi_barcode`?

No. Desde 19.0.2.0.0 este módulo Foundation es independiente y solo publica la
ficha/QR neutral. `kt_product_multi_barcode` gestiona los códigos alternos en
Professional; el bridge opcional `kt_product_public_qr_multi_barcode` los
incorpora a la ficha sin duplicarlos.

## ¿Necesito tener `website_sale` (la tienda en línea) instalado?

No. Solo necesitas el módulo `website` (el sitio web base de Odoo).
`website_sale` es para vender en línea; este módulo solo publica una
página informativa, no un carrito de compras.

## ¿Cualquiera que tenga el enlace puede ver la página?

Sí — es intencional, ese es el propósito (permitir que alguien sin
cuenta de Odoo, escaneando una etiqueta física, vea información
básica). Por eso la página **nunca** muestra proveedor, marketplace,
ni cantidad en stock — solo información que es aceptable que
cualquiera vea.

## ¿Qué pasa si cambio el nombre o la imagen del producto?

La página pública se actualiza automáticamente — no hay caché ni
copia estática de esos datos, se leen en vivo desde el producto cada
vez que alguien visita el enlace.

## ¿El token de acceso se puede regenerar si se filtra o se comparte por error?

Sí — desde la ficha del producto, pestaña "QR público", botón
**"Regenerar enlace público"** (agregado el 05/08/2026). Pide
confirmación antes de aplicar el cambio, porque es irreversible: el
enlace/QR **anterior deja de funcionar de inmediato** y cualquier
etiqueta ya impresa con el código viejo queda inválida (hay que
reimprimirla con el nuevo QR).

Alternativa por shell de Odoo (ya no es necesaria para el uso normal,
pero sigue funcionando para scripts/automatizaciones):

```python
import uuid
producto = env['product.template'].browse(ID_DEL_PRODUCTO)
producto.kt_public_access_token = uuid.uuid4().hex
```

## ¿Funciona si tengo varios dominios apuntando a la misma base de datos?

Sí, ese es justamente uno de los casos que este módulo cubre — ver la
sección correspondiente en el `README.md`. Si tienes un solo dominio
(caso más común), simplemente deja el campo "Sitio web de la página
pública" vacío en cada producto y todo funciona igual sin
configuración adicional.

## ¿Por qué la etiqueta QR no usa una librería externa de Python para generar el código?

Se probaron dos enfoques reales, no solo uno en teoría:

1. **El widget nativo de Odoo** (`t-options="{'widget': 'barcode',
   'symbology': 'QR'}"`) — el mismo que usa `kt_product_multi_barcode`
   para sus propias etiquetas. Funciona bien para valores simples
   (códigos numéricos), pero **falló con una URL completa** — el QR
   resultante quedaba con los caracteres especiales (`:`, `/`)
   corruptos al escanearlo con un lector real, confirmado el
   03/08/2026.
2. **El enfoque final, usado hoy:** construir la ruta manualmente
   (`/report/barcode/?barcode_type=QR&value=...`), codificando la URL
   correctamente con `urllib.parse.quote` antes de insertarla — sin
   agregar ninguna dependencia nueva al servidor, ya que sigue usando
   el mismo generador nativo de Odoo por debajo, solo sin pasar por
   el widget que causaba el problema.

## El QR se ve bien en la página web, pero sale en blanco en el PDF de la etiqueta, ¿por qué?

Le pasó exactamente esto al equipo real (03-04/08/2026): la ruta de
la imagen era **relativa** (`/report/barcode/...`), y el motor que
genera el PDF no resuelve rutas relativas de la misma forma que un
navegador navegando la página en vivo. La corrección usa la URL
**absoluta** (con el dominio completo) — si ves este mismo síntoma en
una versión anterior del módulo, actualiza a la última.

## ¿El código de barras/QR que genera Odoo funciona con cualquier ancho y alto?

Los valores por defecto (`width=600, height=100`) están pensados para
un código de barras **lineal** (ancho y bajo) — si necesitas un QR
(cuadrado), siempre hay que especificar explícitamente un ancho y
alto iguales entre sí (ej. `width=300&height=300`), o el QR sale
aplastado y difícil de escanear.

## Un producto con varias variantes, ¿cómo se ve en la página pública?

Se muestra una sección por cada variante ("Presentaciones disponibles"), cada
una con su código de barras oficial. Si está instalado el bridge Professional,
también muestra sus códigos alternos sin mezclarlos. Esto es porque
el código de barras oficial vive en la **variante**
(`product.product`), no en la plantilla general — un producto con
varias variantes no tiene "un" código oficial único.

## ¿Puedo imprimir etiquetas QR para varios productos a la vez, en una sola hoja?

Todavía no — hoy genera una página de PDF por producto. Ver
`docs/DISENO_IMPRESION_MASIVA.md` para el diseño completo de esta
mejora (junto con soporte ZPL y exportación masiva de PNG),
diseñado pero pendiente de construir.

## ¿Por qué el módulo dice "en desarrollo" si el código está completo?

Porque "código completo" y "probado en un servidor real" son cosas
distintas. Ver `docs/ESTADO.md` para el detalle exacto de qué falta
confirmar antes de considerarlo listo para producción.
