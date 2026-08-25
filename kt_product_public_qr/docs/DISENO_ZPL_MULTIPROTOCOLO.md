# Diseño — Impresión térmica directa: ZPL / EPL / TSPL / DPL

**Estado (04/08/2026): el módulo puente `kt_qr_webkul_print` está
CONSTRUIDO, y la generación de ZPL en sí YA SE CONFIRMÓ CORRECTA con
una prueba real** — se generó el texto ZPL de 3 productos reales
(Acoustic Bloc Screens, Cabinet with Doors, Conference Chair), cada
uno con su bloque `^XA...^XZ` completo, su QR con la URL correcta, y
su nombre — sintaxis y datos correctos, confirmado.

## ✅ RESUELTO (05/08/2026) — ver `kt_qr_webkul_print/docs/ESTADO.md`

**Actualización:** lo que esta sección describía como "pendiente
real, sin resolver" (el reporte no aparecía seleccionable al
configurar una impresora) **se resolvió el 05/08/2026**, un día
después de escrita esta sección — el detalle completo de la causa
real y la solución vive en `kt_qr_webkul_print/docs/ESTADO.md` (el
módulo puente que efectivamente implementa esta impresión ZPL), no
aquí. El contenido original de esta sección se conserva abajo como
registro histórico de la investigación, pero **ya no representa el
estado actual**.

### (Histórico, 04/08/2026) El reporte NO aparecía como opción seleccionable al configurar una impresora

En `Print Direct → Printers` (campo donde normalmente se
le asignan reportes a una impresora, junto a los que ya usan para
facturas/etiquetas de lote). Se había verificado que el reporte en sí
estaba perfectamente configurado en la base de datos
(`printerType = 'ZPL'`, `report_type = 'qweb-text'`,
`binding_model_id = product.template`, todo correcto) — el problema
parecía estar en el **dominio/filtro** que usa el selector de
reportes de la impresora en la interfaz de Webkul, no en nuestro
reporte.

**Siguiente paso concreto para investigar esto:** revisar
`wk_odoo_direct_print/models/wk_hostmachine.py` (10KB, el archivo
más grande de `models/` — probablemente ahí vive el modelo real de
la impresora, `wk.printer`, ya que no existe un archivo separado
`wk_printer.py`) — específicamente buscar el campo `report_ids` y
confirmar si tiene algún `domain=` que nuestro reporte no esté
cumpliendo (ej. algo relacionado a la compañía, a un grupo de
seguridad, o a otro campo que no hayamos configurado en nuestro
registro). Esto quedó identificado pero sin revisar todavía —
retomar desde aquí.

**Confirmado que SÍ funciona (no es un problema de generación):**
llamar al reporte directamente (sin pasar por el selector de la
impresora) genera el ZPL correcto — el bloqueo está específicamente
en la UI de asignación, no en el reporte en sí.

El resto de este documento (protocolos alternos EPL/TSPL/DPL, el
camino "sin Webkul") sigue siendo solo diseño, sin construir.

## ⭐ Hallazgo clave (04/08/2026) — cambia todo el diseño, para mucho más simple

El usuario ya tiene instalado **`wk_odoo_direct_print`** (Webkul "Print
Direct"), revisado directamente su código fuente real. Esto cambia
por completo el alcance de lo que hay que construir:

- Ya soporta reportes de tipo **texto plano** (`report_type =
  'qweb-text'`) — verificado en `controllers/report.py`: cuando el
  tipo de impresora NO es ESCPOS (o sea, para ZPL y similares), el
  texto generado por el reporte **se envía tal cual, sin ninguna
  transformación**, directo a la impresora vía `method: 'print-raw'`.
- Ya resuelve **todo** lo de conexión: la app de escritorio/móvil se
  conecta a Odoo por WebSocket (`bus.bus._sendone`, el mismo canal de
  notificaciones en tiempo real nativo de Odoo) — exactamente el
  mismo problema de "servidor en la nube, impresora en red local" que
  ya identificamos, ya resuelto por ellos.
- Ya tiene modelo de impresora (`wk.printer`, con campo `printerType`
  que incluye `'ZPL'` como opción real, confirmado en
  `models/stock_picking.py` y `models/default_printer.py`), cola de
  trabajos (`print.jobs`), registro de máquinas conectadas
  (`wk.hostmachine`), y hasta reglas de auto-impresión
  (`autoprint.rule`).

**Conclusión: no hay que construir `kt.label.printer`, ni sockets de
red, ni cola propia — nada de eso.** Todo el diseño de abajo (el
modelo `kt.label.printer`, el mecanismo de envío por socket) queda
**obsoleto** para el caso de tener Webkul instalado — se conserva
más abajo solo como referencia, por si algún día hace falta un
camino independiente sin depender de un módulo de terceros de pago.

### Lo único que de verdad hace falta construir

**Un solo reporte QWeb de tipo texto** (`report_type='qweb-text'`),
enganchado a `product.template`, cuya plantilla renderiza el ZPL de
la etiqueta (reutilizando el mismo "traductor" ya diseñado más
abajo) — usando texto plano de Python/QWeb, sin ningún HTML ni PDF
de por medio. Webkul se encarga de todo lo demás automáticamente, en
cuanto el usuario:
1. Configure una impresora en `wk.printer` con `printerType = 'ZPL'`.
2. Asigne nuestro reporte nuevo a esa impresora
   (`printer.report_ids`).
3. Use el menú normal de Imprimir del producto — exactamente el mismo
   flujo que ya usa hoy para imprimir el PDF de la etiqueta QR.

### Confirmado con el código fuente real de Webkul (04/08/2026) — los últimos detalles que faltaban

**`printerType`** es un campo `Selection` que Webkul agrega a
`ir.actions.report` (`[('ZPL', 'ZPL'), ('ESCPOS', 'ESCPOS'), ('PDF', 'PDF')]`)
— **calculado automáticamente**, pero con una regla sutil e
importante:

```python
def _compute_printer_type(self):
    for rec in self:
        if rec.report_type == "qweb-pdf":
            rec.printerType = "PDF"
        elif rec.report_type == "qweb-text":
            if 'ZPL' in rec.name:
                rec.printerType = "ZPL"
```

**Si el reporte es `qweb-text` pero la palabra "ZPL" no aparece
literalmente en su `name`, `printerType` se queda vacío** — no hay
ningún valor por defecto para ese caso. Esto confirma por qué la
documentación de Webkul nombra sus reportes como "Lots/Serial Number
**(ZPL)**": no es solo un nombre bonito, es un requisito funcional
real para que el sistema lo detecte solo.

**Decisión de diseño, para no depender de un truco de nomenclatura:**
nuestro reporte se va a llamar algo como "Etiqueta QR pública
(ZPL)" (cumple la convención de todas formas, por claridad), **y
además** se fija `printerType = 'ZPL'` explícitamente en el XML del
propio registro — no dejarlo completamente a la detección automática
por nombre, para no arriesgar que un cambio de texto rompa la
detección sin que se note.

**`printer.report_ids`** — confirmado como un campo Many2many real en
`wk.printer` (visible en cómo Webkul lo busca:
`wkprinter.search([..., ('report_ids', 'in', [report.id])])`) — el
usuario simplemente selecciona nuestro reporte ahí, desde la ficha de
la impresora, como cualquier otro reporte — no hace falta ningún
registro especial de nuestra parte más allá de que el reporte exista.

### Diseño del bucle para varios productos en un solo trabajo de impresión

Dado que `_render_qweb_text` recibe una lista de `active_ids` (varios
productos a la vez, si se seleccionan varios), la plantilla debe
recorrerlos y concatenar un bloque `^XA...^XZ` completo por cada uno
— reutilizando el mismo patrón de `_get_report_values` +
`build_label_list` ya construido para la cuadrícula en PDF, solo que
en vez de armar una tabla HTML, se concatena texto plano:

```python
class ReportKtPublicQrZpl(models.AbstractModel):
    _name = 'report.kt_public_qr_webkul_print.report_kt_public_qr_zpl'

    def _get_report_values(self, docids, data):
        products = self.env['product.template'].browse(docids)
        return {'products': products}
```

Y la plantilla (texto plano, sin ninguna etiqueta HTML — recordar que
`_render_qweb_text` usa el mismo motor QWeb que el HTML, pero el
resultado se interpreta como texto tal cual, no como marcado):

```xml
<template id="report_kt_public_qr_zpl_document">
    <t t-foreach="products" t-as="product">^XA
^CI28
^FO80,80^BQN,2,8^FDQA,<t t-esc="product.kt_public_qr_url"/>^FS
^FO80,320^A0N,30,30^FD<t t-esc="product.name"/>^FS
^XZ
</t>
</template>
```

**`^CI28`** (agregado en el diseño, confirmado en la documentación
pública de ZPL): activa la codificación UTF-8 en la impresora — sin
esto, los nombres de producto con tildes/ñ (comunes en español)
podrían imprimirse mal.

### Por qué esto debería vivir en un módulo puente aparte, no directo en `kt_product_public_qr`

`wk_odoo_direct_print` es un **módulo comercial de pago** de Webkul
— no todo el que use `kt_product_public_qr` lo va a tener instalado.
Igual que se hizo con `ecommerce_barcode_search` /
`kt_ecommerce_barcode_search_patch`, este reporte ZPL debería vivir
en un módulo nuevo y opcional (ej. `kt_public_qr_webkul_print`), que
dependa de AMBOS (`kt_product_public_qr` + `wk_odoo_direct_print`) —
así, quien no tenga Webkul instalado ni se entera de que existe esta
opción, y quien sí lo tenga, la ve aparecer sola.

---

Amplía el punto 2 de `DISENO_IMPRESION_MASIVA.md` (dentro de
`kt_product_public_qr`) — en vez de soportar solo ZPL, este diseño
cubre los 4 protocolos de impresión térmica directa más comunes,
usando una arquitectura de "traductores" para no repetir la lógica de
armado de etiqueta 4 veces.

---

## Impresora real disponible para las pruebas (confirmado, no genérico)

Jaltech "Impresora de códigos de barra USB/LAN" (código 40146,
referencia JAL CO-B) — un modelo genérico (OEM común, vendido bajo
varias marcas) que trae de fábrica soporte para **los 4 protocolos
de este diseño a la vez** (el usuario elige cuál usar, no hay que
elegir uno solo de antemano). Especificaciones reales relevantes:

- **Resolución:** 203 DPI (→ 1mm ≈ 8 puntos/dots — importante para
  convertir milímetros a las unidades que estos protocolos usan
  internamente).
- **Ancho máximo de impresión:** 104mm.
- **Interfaz:** USB **y LAN (RJ45)** — confirma que el diseño de
  "enviar directo por red al puerto 9100" (ver más abajo) aplica
  directo a este modelo real, sin necesitar nada adicional.
- **Símbolos 1D soportados:** Code 39, Code 93, Code 128 UCC, Code
  128 (subconjuntos A/B/C), Codabar, Intercalado 2 de 5, EAN-8,
  EAN-13, EAN-128, UPC-A, UPC-E, EAN/UPC complemento 2, complemento
  de dígitos, MSI, Plessey, POSTNET, China Post.
- **Símbolos 2D soportados:** PDF-417, MaxiCode, DataMatrix, código
  QR, Aztec.

**Esto amplía el diseño original** (que solo contemplaba QR) — dado
que la impresora real puede dibujar cualquiera de estos símbolos, la
descripción abstracta de la etiqueta (ver más abajo) debería soportar
más tipos de `elements`, no solo `'qr'`.

---

## Los 4 protocolos, confirmados con fuentes reales (no de memoria)

Cada uno con su propia sintaxis para las mismas 4 operaciones básicas
que necesitamos (iniciar etiqueta, dibujar texto, dibujar un QR,
mandar a imprimir):

| Protocolo | Fabricante típico | Iniciar/limpiar | Texto | QR | Imprimir |
|---|---|---|---|---|---|
| **ZPL** (Zebra Programming Language) | Zebra | `^XA` | `^FO`+`^A`+`^FD`+`^FS` | `^FO`+`^BQ`+`^FD` | `^XZ` |
| **EPL/EPL2** (Eltron) | Zebra/Eltron (modelos antiguos) | `N` (limpia buffer) | `A x,y,rot,fuente,h,v,rev,"texto"` | `b x,y,tipo,...,"dato"` (minúscula, para 2D) | `P1` |
| **TSPL/TSPL2** | TSC | `CLS` (tras `SIZE`/`GAP`) | `TEXT x,y,"fuente",rot,h,v,"texto"` | `QRCODE x,y,nivel,tamaño,modo,rot,"dato"` | `PRINT 1,1` |
| **DPL** (Datamax) | Datamax/Honeywell | `<STX>L` (entra a modo formato) | Estructura de registro (`<STX>` + campo) | Estructura de registro para código 2D | `E` (termina formato e imprime) |

**Diferencia importante de DPL frente a los otros 3:** los otros tres
son lenguajes de texto plano, línea por línea, relativamente fáciles
de generar como un string simple. DPL usa una estructura basada en el
carácter de control `<STX>` (0x02) para delimitar cada bloque —
genuinamente más distinto de los otros tres, más parecido a un
protocolo binario que a texto plano.

---

## La arquitectura — una descripción abstracta, 4 traductores

En vez de construir la etiqueta directamente en el lenguaje de cada
impresora, se describe de forma abstracta (un diccionario de
Python, sin ningún comando de ningún protocolo todavía). Ampliado
(04/08/2026) para cubrir cualquier símbolo 1D/2D que la impresora
real soporte, no solo QR:

```python
label = {
    'width_mm': 60,
    'height_mm': 50,
    'elements': [
        # 2D — símbolos confirmados en la impresora real: QR, PDF-417,
        # MaxiCode, DataMatrix, Aztec.
        {'type': '2d', 'symbology': 'qr', 'x_mm': 15, 'y_mm': 5,
         'size_mm': 30, 'value': 'https://...'},

        # 1D — símbolos confirmados: Code128, EAN-13, EAN-8, UPC-A,
        # UPC-E, Code39, Code93, Codabar, Intercalado 2 de 5, MSI,
        # Plessey, POSTNET, China Post (entre otros).
        {'type': '1d', 'symbology': 'code128', 'x_mm': 5, 'y_mm': 40,
         'height_mm': 8, 'value': '20777660000018'},

        {'type': 'text', 'x_mm': 2, 'y_mm': 2, 'font_size_mm': 3,
         'value': 'Nombre del producto'},
    ],
}
```

**Nota de diseño importante:** el `symbology` que se le pide a la
impresora (ej. `'code128'`) es un concepto **separado** de los tipos
de código alterno que ya maneja `kt_product_multi_barcode`
(`code_type` en `kt.product.multi.barcode`) — aunque en la práctica
casi siempre van a coincidir 1 a 1 (si el código alterno es
"EAN-13", lo lógico es pedirle a la impresora que dibuje un EAN-13
también), conviene no asumir automáticamente que son intercambiables
sin revisar — no todos los símbolos que reconoce
`kt_product_multi_barcode` para BUSCAR un producto tienen por qué
tener sentido para IMPRIMIR (ej. un "SSCC" es un identificador de
paquete/logística, no algo que normalmente se imprima como etiqueta
de producto individual).

Y luego, un **traductor por protocolo** (patrón "adaptador") convierte
esa misma descripción al texto/comandos específicos de cada
impresora:

```python
class ZplRenderer:
    def render(self, label: dict) -> bytes: ...

class EplRenderer:
    def render(self, label: dict) -> bytes: ...

class TsplRenderer:
    def render(self, label: dict) -> bytes: ...

class DplRenderer:
    def render(self, label: dict) -> bytes: ...
```


**Ventaja real de este diseño:** agregar un producto nuevo (ej. un
código de barras en vez de un QR, o un logo) solo implica agregar un
nuevo tipo de `elements` y enseñarle a los 4 traductores a dibujarlo
— la lógica de "qué productos, qué cantidad, qué tamaño de etiqueta"
(ya resuelta en `kt_label_printing`, reutilizando `kt.label.size` y
`kt_label_grid_utils.py`) no cambia en absoluto.

### Ejemplo concreto — el mismo QR, en los 4 protocolos

Para un QR con el valor `https://nexoferretero.com/producto/abc123`,
en una posición aproximada (10mm, 10mm) con tamaño 30mm:

**ZPL:**
```
^XA
^FO80,80^BQN,2,8^FDQA,https://nexoferretero.com/producto/abc123^FS
^XZ
```

**EPL2** (la `b` en minúscula es el comando de código 2D — distinto
de la `B` mayúscula, que es para códigos de barras lineales de una
sola dimensión):
```
N
b80,80,Q,50,,"https://nexoferretero.com/producto/abc123"
P1
```

**TSPL/TSPL2:**
```
SIZE 60 mm,50 mm
CLS
QRCODE 80,80,M,8,A,0,"https://nexoferretero.com/producto/abc123"
PRINT 1,1
```

**DPL** (estructura de registro, más distinta de las otras 3 —
requiere el carácter de control STX, no reproducible como texto
simple en este documento; se arma con bytes, no con un string
literal):
```
<STX>L
1112110001000080008000000https://nexoferretero.com/producto/abc123
E
```

*(Los valores exactos de coordenadas/parámetros arriba son
ilustrativos — la implementación real deberá probarse contra una
impresora física de cada protocolo, o al menos un emulador, antes de
darse por buena — ningún protocolo de estos se puede validar
"leyendo el manual" con la misma certeza que el código fuente de
Odoo.)*

---

## Cómo se conecta con lo ya construido (`kt_label_printing`)

> **Nota (04/08/2026):** las siguientes secciones (hasta "Prioridad
> sugerida") describían un modelo de impresora PROPIO y un envío por
> socket de red construido desde cero — ver el hallazgo al inicio de
> este documento: con `wk_odoo_direct_print` ya instalado, nada de
> esto hace falta construirlo, Webkul ya lo resuelve. Se conserva
> como referencia para el escenario alterno (sin Webkul instalado),
> no como el plan principal.

- El ancho/alto de la etiqueta (`width_mm`/`height_mm` en la
  descripción abstracta) sale directo de `kt.label.size` —
  reutilizado tal cual, sin cambios.
- El QUÉ imprimir por producto (la URL pública, el nombre) sigue
  siendo responsabilidad de cada módulo dependiente
  (`kt_product_public_qr` decide "QR con esta URL, texto con este
  nombre") — igual que ya diseñamos para el PDF.

### Un hueco real de diseño, encontrado al revisar `kt.label.size` con cuidado

`kt.label.size` (ya construido) solo tiene **un** tamaño de
"contenido principal" (`content_size_mm`) — pensado para el caso
simple de "un QR grande + texto arriba/abajo", que es exactamente lo
que necesitaba el PDF. Pero la descripción abstracta de arriba
permite **varios elementos**, cada uno con su propia posición X/Y —
algo que `kt.label.size`, tal como está, no describe.

**Decisión de diseño (para no sobre-construir esto de entrada):**
para la primera versión de ZPL/EPL/TSPL/DPL, **no** se construye un
diseñador visual de plantillas con posiciones libres — se reutiliza
el mismo patrón simple ya usado en el PDF (un símbolo principal
centrado + una línea de texto arriba), calculando automáticamente las
posiciones X/Y a partir de los 3 números que `kt.label.size` ya
tiene, igual que ya hace la plantilla QWeb del PDF. Si más adelante
hace falta un diseño más libre (varios elementos en posiciones
arbitrarias), sería un modelo nuevo y aparte (ej.
`kt.label.template`, con líneas hijas por elemento) — no construir
esto ahora, sin una necesidad real confirmada primero.

### Dónde vive la decisión de "qué protocolo, qué impresora"

- El asistente de impresión (`product.label.layout`, el mismo que ya
  usamos para PDF y para PNG) ganaría una opción más de destino: en
  vez de "PDF" o "Descargar ZIP de PNG", una tercera — "Enviar a
  impresora térmica" — que muestra un selector de
  `kt.label.printer` (configurada de antemano) en vez de un tamaño de
  papel.
- Esto significa que, desde el punto de vista del usuario, es **una
  opción más dentro del mismo flujo ya conocido** (seleccionar
  productos → Acción → Imprimir/Exportar), no una pantalla
  completamente aparte.

### Manejo de errores de red (algo que el resto del proyecto no necesitaba)

A diferencia de generar un PDF o un PNG (que siempre funciona, porque
todo pasa dentro del propio servidor de Odoo), enviar por red a una
impresora física puede fallar por razones reales: la impresora está
apagada, sin papel, en otra red, o la IP configurada es incorrecta.
El diseño necesita contemplar esto explícitamente:

- Un tiempo de espera corto (ej. 3-5 segundos) al intentar conectar
  por socket — para no dejar la pantalla de Odoo "colgada" esperando
  indefinidamente si la impresora no responde.
- Un mensaje de error claro y accionable (`UserError`) si falla la
  conexión — no un traceback técnico sin contexto.
- Considerar, como respaldo automático, ofrecer la descarga del
  archivo si el envío por red falla — así el usuario no se queda sin
  ninguna opción solo porque la red falló en ese momento puntual.

## Modelo nuevo — `kt.label.printer` (configuración de la impresora)

```python
class KtLabelPrinter(models.Model):
    _name = 'kt.label.printer'

    name = fields.Char()
    protocol = fields.Selection([
        ('zpl', 'ZPL (Zebra)'),
        ('epl', 'EPL/EPL2 (Eltron / Zebra antiguas)'),
        ('tspl', 'TSPL/TSPL2 (TSC)'),
        ('dpl', 'DPL (Datamax/Honeywell)'),
    ], required=True)
    connection_type = fields.Selection([
        ('network', 'Red (IP)'),
        ('download', 'Descargar archivo'),
    ], default='download', required=True)
    ip_address = fields.Char()
    port = fields.Integer(default=9100)  # puerto "raw" estándar, compartido por los 4 protocolos
    kt_label_size_id = fields.Many2one('kt.label.size', required=True)
```

## Mecanismo de envío

- **Descarga de archivo:** simplemente guardar los bytes generados
  con la extensión correspondiente (`.zpl`, `.epl`, `.tspl`, `.dpl`)
  — el usuario lo manda a imprimir con el software propio de su
  impresora.
- **Envío directo por red:** un socket TCP simple al puerto 9100 de
  la IP configurada (`socket.socket(...).sendall(comandos)`) — es el
  mecanismo estándar de facto compartido por los 4 protocolos para
  impresión en red ("raw printing"/estilo JetDirect), sin necesitar
  ningún driver especial ni librería de terceros.

---

## Honestidad sobre el nivel de certeza de este diseño

**Lo que SÍ quedó verificado con certeza real (04/08/2026):** todo
el mecanismo de conexión/envío — revisado línea por línea contra el
código fuente real de `wk_odoo_direct_print`, igual de riguroso que
el resto de este proyecto con el código de Odoo.

**Lo que sigue siendo menos seguro:** la sintaxis exacta de los 4
protocolos en sí — no son de Odoo ni de Webkul, son lenguajes
propietarios de cada fabricante de impresora, documentados en
manuales públicos que sí revisé, pero:

- Los parámetros exactos (unidades de posición, escalas, niveles de
  corrección de error del QR) varían según el **modelo específico**
  de impresora dentro de cada protocolo — lo de arriba es
  representativo, no una garantía universal.
- **Nada de esto se puede probar sin una impresora física real** (o
  al menos un emulador confiable) de cada protocolo — a diferencia
  del resto del proyecto, donde siempre pudimos verificar contra
  Odoo corriendo de verdad.

## Prioridad sugerida si se decide construir

**Actualizado (04/08/2026), tras confirmar `wk_odoo_direct_print`:**
la ruta más corta y de menor riesgo cambió por completo respecto a
lo que se pensaba antes.

1. **Construir el módulo puente** (`kt_public_qr_webkul_print` o el
   nombre que se decida) — un solo reporte QWeb tipo texto (ver
   arriba) que genera ZPL para el QR público. Esto reutiliza TODA la
   infraestructura de conexión/impresora/cola ya construida y
   funcionando de Webkul — el trabajo real es mínimo comparado con
   lo que se pensaba originalmente.
2. **Probar con la impresora real** (Jaltech 40146/JAL CO-B, que ya
   confirmamos soporta ZPL) — configurando una impresora en
   `wk.printer` con `printerType = 'ZPL'`, asignándole el reporte
   nuevo, y usando el flujo normal de Imprimir.
3. Los otros 3 protocolos (EPL, TSPL, DPL) — solo si hace falta una
   impresora que NO soporte ZPL en algún momento futuro; con Webkul
   ya resolviendo la conexión, agregar los otros 3 sería repetir el
   mismo patrón simple (un reporte de texto más, con su propio
   "traductor"), no un esfuerzo grande.
4. El camino "sin Webkul" (secciones de `kt.label.printer` y envío
   por socket, más arriba) — dejarlo completamente de lado a menos
   que en algún momento se necesite una solución que no dependa de
   un módulo de terceros de pago.
