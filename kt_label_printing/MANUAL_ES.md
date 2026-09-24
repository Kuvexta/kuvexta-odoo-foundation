# kt_label_printing — Manual de uso

Este módulo administra los **tamaños de etiqueta** que comparten los
módulos que imprimen etiquetas (hoy: `kt_product_public_qr`), y trae
además su propia salida: la **rejilla PDF de etiquetas de producto**,
que se imprime desde el asistente de etiquetas de Odoo con la opción
**«Rejilla PDF Kuvexta»**.

## Índice

1. [Qué es y para qué sirve](#1-qué-es-y-para-qué-sirve)
2. [Ejemplo: crear un tamaño de etiqueta propio](#2-ejemplo-crear-un-tamaño-de-etiqueta-propio)
3. [Preguntas frecuentes](#3-preguntas-frecuentes)

---

## 1. Qué es y para qué sirve

Cuando imprimes etiquetas en una hoja (por ejemplo, desde
`kt_product_public_qr`), necesitas describirle al sistema **cómo es
tu papel/rollo físico**: qué tan grande es cada etiqueta, qué tan
grande es la hoja completa, y cuánto margen dejar — para que calcule
solo cuántas etiquetas caben por hoja (columnas × filas), sin que
tengas que hacer esa cuenta a mano.

Trae **3 tamaños de ejemplo** ya cargados, disponibles apenas
instalas el módulo:

| Nombre | Etiqueta | Hoja | Aproximadamente |
|---|---|---|---|
| A4 - Cuadrado | 63×55mm | A4 (210×297mm) | 15 por hoja |
| A4 - Pequeño | 40×35mm | A4 (210×297mm) | ~35 por hoja |
| Rollo térmico 4 pulgadas | 95×95mm | 101.6mm × 2000mm (una columna continua) | Una etiqueta tras otra |

## 2. Ejemplo: crear un tamaño de etiqueta propio

**Caso de ejemplo:** tienes un rollo térmico de etiquetas de
50×30mm, en una impresora de 2 pulgadas de ancho (58mm reales de
papel).

1. Ve a `Inventario → Control de inventario → Tamaños de etiqueta`,
   botón **Nuevo**.
2. **Nombre**: "Rollo térmico 2 pulgadas 50x30mm" (o el nombre que
   prefieras — es solo para identificarlo en la lista).
3. **Ancho de la etiqueta**: `50` mm. **Alto de la etiqueta**: `30`
   mm.
4. **Tamaño del contenido principal**: el tamaño del QR/código de
   barras dentro de la etiqueta — por ejemplo `20` mm, dejando
   espacio para texto arriba/debajo.
5. **Ancho de la hoja**: `58` mm (el ancho real de tu rollo).
   **Alto de la hoja**: un número grande, ej. `2000` mm — así el PDF
   resultante trae muchas etiquetas seguidas, aprovechando el largo
   real disponible del rollo (no es un límite real, solo cuánto
   "papel" simula el PDF).
6. **Margen de la hoja**: `2` mm (ajusta según tu impresora — el
   margen que no se puede imprimir en los bordes).
7. Guarda — los campos **Columnas** y **Filas** se calculan solos
   (en este ejemplo, probablemente 1 columna, ya que 50mm caben una
   sola vez en 58mm de ancho útil).
8. Al imprimir etiquetas —con la opción «Rejilla PDF Kuvexta» o
   desde otro módulo que use estos tamaños, como
   `kt_product_public_qr`—, este nuevo tamaño aparece disponible
   para elegir, junto con los 3 de ejemplo.

## 3. Preguntas frecuentes

**¿Puedo editar o borrar los 3 tamaños de ejemplo?**
Sí — son solo sugerencias de partida, edítalos o bórralos si no
corresponden a tu papel real. No afectan ninguna etiqueta ya
impresa (los PDF generados no dependen del registro después de
creados).

**¿Este módulo imprime algo si lo instalo solo?**
Sí — trae **«Etiquetas de producto (cuadrícula PDF)»**, que genera una
hoja con una cuadrícula de etiquetas: en recepción de mercancía se
recibe un lote, y así la hoja se imprime de una vez en lugar de abrir
una imagen por artículo.

Para usarla:

1. Selecciona los productos y pulsa **Imprimir etiquetas**.
2. En **Formato**, elige **«Rejilla PDF Kuvexta»**.
3. En **Tamaño de etiqueta**, elige el tamaño de tu papel. Solo aparece
   con esta opción, y es obligatorio.
4. Pon las copias y pulsa **Imprimir**.

**Desde una recepción**, el botón **Imprimir etiquetas** de la operación
pregunta qué etiquetas quieres: elige **Etiquetas de producto** —la opción
por defecto— y se abre el mismo asistente. Con **«Cantidades de la
operación»** sale **una etiqueta por unidad recibida** de cada producto, las
mismas cantidades que usa Odoo para sus etiquetas estándar.

**Productos con lote o número de serie.** Su etiqueta lleva **los dos**: el
código de barras **del producto** —el mismo que tendría sin lote— y, debajo,
en texto, el lote o el serial:

- **«Lote: L-2026-0917»** si el producto se controla por lotes;
- **«S/N: SN-0001»** si se controla por número de serie, una etiqueta por
  serial;
- **«Lote/S/N: X»** si el producto ya no tiene seguimiento pero llegó con
  lote (pasa si se cambió su configuración después de recibir).

Así la caja se escanea como cualquier otra del mismo producto, y el lote se
lee a la vista. **Es distinto de las etiquetas estándar de Odoo**, que
imprimen solo el código del lote.

> **Límite de esta versión:** el lote o serial va **solo en texto**, sin su
> propio código de barras. Si necesitas escanearlo, tecléalo. Si un lote es
> tan largo que no cabe, se corta con puntos suspensivos («…») sin mover el
> resto de la hoja.

Para que salgan los lotes, la recepción tiene que tener **asignados los lotes
o seriales, con su cantidad**, antes de imprimir; y el producto, la unidad de
medida **Unidades**. Con otra unidad Odoo imprime una sola etiqueta y sin
lote. Los lotes y números de serie se activan en *Inventario → Ajustes →
Lotes y números de serie*.

Si en vez de **Etiquetas de producto** eliges **Etiquetas de lote/SN**, se
abre el asistente estándar de Odoo para etiquetas de lote, que este módulo no
modifica.

**Cada etiqueta es de la variante**: una camisa talla M y la misma en talla L
salen cada una con **su** código de barras. Si imprimes desde la ficha de un
producto con variantes, salen todas sus variantes, cada una con las copias
indicadas.

**Todo sale del tamaño elegido**: cuántas columnas y filas hay por
hoja, cuánto mide cada etiqueta, cuánto mide el código de barras —de
ancho, el «tamaño del contenido principal»; de alto, lo que deja libre
el texto— y el tamaño de la propia hoja del PDF, con su margen. Dos
tamaños distintos dan hojas distintas. Los demás formatos del asistente
siguen imprimiendo las etiquetas estándar de Odoo, sin cambios.

Cada etiqueta lleva **el código de barras, el nombre y la referencia
interna**. No lleva precio a propósito: un precio impreso caduca, y
una etiqueta con precio viejo es peor que una sin él.

Otros módulos pueden seguir definiendo su propio contenido —qué
código, qué texto— y reutilizar de aquí los tamaños y el cálculo de la
cuadrícula.

**¿Y si un producto no tiene código de barras?**
Es frecuente en ferretería —tornillería suelta, cortes a medida—, y
**ningún producto se queda sin etiqueta**. El sistema va probando en
este orden:

1. **Si tiene código de barras**, se imprime ese.
2. **Si no, pero tiene referencia interna**, se imprime la referencia
   como código de barras, y la etiqueta lleva la marca **SKU** al lado
   para que nadie la confunda con el código del fabricante.
3. **Si no tiene ninguno de los dos**, la etiqueta sale igual con su
   nombre y su referencia, sin gráfico: legible y cotejable a mano,
   aunque no se pueda escanear.

Cuántos saldrán por el caso 2 y por el caso 3, y cuáles, lo **avisa
el asistente antes de imprimir**, con la opción «Rejilla PDF Kuvexta»
elegida —con los formatos estándar no aparece, porque esos no aplican
este orden—. No va en la hoja: **la hoja lleva solo etiquetas**,
porque en papel adhesivo cualquier aviso impreso ocuparía celdas y
desplazaría la cuadrícula.

**¿Necesito algo instalado en el servidor para el PDF?**
Sí: **`wkhtmltopdf`**, el programa que Odoo usa para convertir a PDF.
El módulo lo declara, así que Odoo **no deja instalarlo** si falta, en
vez de instalarse y fallar al imprimir.

**¿Cómo sé qué tamaño de hoja poner para un rollo continuo (sin
hojas fijas como A4)?**
Pon el ancho real del rollo en "Ancho de la hoja", y un número
grande (ej. 2000mm) en "Alto de la hoja" — el sistema no necesita
saber el largo real del rollo, solo genera tantas etiquetas seguidas
como necesites, una tras otra en esa "hoja" larga y angosta.

---

<sub>Nombre canónico de este archivo: `kt_label_printing/MANUAL_ES.md`. Alias de coordinación, en minúsculas porque el patrón de scopes no admite mayúsculas: `repo/source/file/kt_label_printing/manual_es.md`.</sub>
