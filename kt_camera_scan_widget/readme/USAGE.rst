En cualquier documento que integre este widget (por ejemplo, una orden de
compra con ``kt_scanflow_documents`` instalado), aparece la opción de
"escanear con cámara" junto a la opción de lector físico:

* Al activarla, se abre un modal con el video de la cámara del dispositivo.
* Apuntar la cámara al código: se decodifica automáticamente, sin necesidad
  de tocar la pantalla.
* Un sonido y una vibración confirman cada escaneo exitoso — se puede seguir
  escaneando el siguiente producto sin mirar la pantalla.
* Si el dispositivo soporta linterna, aparece un botón para encenderla o
  apagarla.
* Si un código no se puede leer, hay un campo de entrada manual como
  respaldo, sin cerrar el modal.

El motor de decodificación se elige automáticamente según el navegador —
esto es transparente para el usuario, no requiere ninguna configuración por
su parte.

**Ejemplo práctico — comprador en la bodega de un proveedor, sin
lector físico:**

1. Desde el celular, abrir la orden de compra en borrador (misma
   sesión de Odoo, en el navegador del teléfono).
2. Tocar "Escanear con cámara" junto al campo de escaneo.
3. Apuntar la cámara al código impreso en la caja del producto — un
   beep y una vibración corta confirman que se leyó.
4. La línea se agrega sola; sin bajar el celular, apuntar al siguiente
   producto.
5. Si un código está borroso o dañado y no decodifica tras varios
   segundos, usar el campo de texto de respaldo dentro del mismo modal
   para escribirlo a mano, sin cerrar la cámara.

**Qué motor se usó en cada caso (transparente para el usuario, mencionado
aquí solo para quien dé soporte técnico):** en un celular Android con
Chrome, el escaneo lo resuelve el motor nativo del navegador
(``BarcodeDetector``, el más rápido). En un iPhone con Safari (que no
lo soporta), el mismo modal funciona igual, pero por debajo usa el
motor de respaldo (ZBar compilado a WebAssembly, cargado solo en ese
caso — no se descarga nada de más en un Android con Chrome).
