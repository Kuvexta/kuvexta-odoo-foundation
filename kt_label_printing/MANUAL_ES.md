# kt_label_printing — Manual de uso

Este es un módulo de **infraestructura compartida** — no imprime
nada por sí solo, no tiene sentido instalarlo aparte de otro módulo
que lo use (hoy: `kt_product_public_qr`). Este manual explica lo
único que sí configuras directamente aquí: los **tamaños de
etiqueta**.

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
8. Al imprimir etiquetas desde el módulo que las usa (ej.
   `kt_product_public_qr`), este nuevo tamaño aparece disponible
   para elegir, junto con los 3 de ejemplo.

## 3. Preguntas frecuentes

**¿Puedo editar o borrar los 3 tamaños de ejemplo?**
Sí — son solo sugerencias de partida, edítalos o bórralos si no
corresponden a tu papel real. No afectan ninguna etiqueta ya
impresa (los PDF generados no dependen del registro después de
creados).

**¿Este módulo imprime algo si lo instalo solo?**
No — no tiene ningún menú de "imprimir", ninguna acción de reporte
propia. Solo trae la administración de tamaños; el contenido real de
la etiqueta (qué código, qué texto) lo define el módulo que lo usa.

**¿Cómo sé qué tamaño de hoja poner para un rollo continuo (sin
hojas fijas como A4)?**
Pon el ancho real del rollo en "Ancho de la hoja", y un número
grande (ej. 2000mm) en "Alto de la hoja" — el sistema no necesita
saber el largo real del rollo, solo genera tantas etiquetas seguidas
como necesites, una tras otra en esa "hoja" larga y angosta.
