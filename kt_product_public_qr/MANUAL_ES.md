# Manual operativo — KT Product Public QR

## Propósito y seguridad

Publica una ficha de producto sin inicio de sesión mediante un token aleatorio y
genera QR imprimibles. Nunca debe exponer stock, proveedor, canal ni información
interna. El bridge Professional puede añadir códigos alternos autorizados.

## Configuración

En una base de un dominio no se requiere configuración. En multiwebsite asigne el
sitio dueño en la pestaña **QR público** del producto. Verifique el dominio y la
redirección antes de imprimir etiquetas.

## Uso

1. Abra Inventario → Productos.
2. Previsualice **Página pública**.
3. Use la acción de impresión de etiqueta QR.
4. Escanee desde un dispositivo sin sesión y compruebe solo los datos aprobados.
5. Para invalidar un enlace, regenere el token y reimprima las etiquetas.

Antes de producción ejecute actualización, prueba de acceso anónimo, multiempresa,
multiwebsite, impresión y dispositivo real. ZPL/Webkul se valida por separado con
licencia del cliente. Consulte también `docs/ESTADO.md` y `docs/FAQ.md`.

Código/manual: `Kuvexta/kuvexta-odoo-foundation@19.0`; diseño transversal:
`Kuvexta/kuvexta-odoo-knowledge`.
## Autoridad documental y mejora continua

- Código y operación de este addon: `Kuvexta/kuvexta-odoo-foundation@19.0`.
- Investigación, diseños, FAQ/PQR, incidentes y lecciones transversales:
  `Kuvexta/kuvexta-odoo-knowledge` mediante `INDEX.yaml` y `CATALOG.yaml`.
- Composición instalable y rollback: bundle exacto de
  `Kuvexta/kuvexta-odoo-integration`.

La copia retenida en Source es evidencia congelada. Toda mejora se propone aquí
y debe actualizar manual, pruebas y comprobante del árbol cuando corresponda.
Los ensayos externos aplicables no se consideran cerrados por una prueba local.
