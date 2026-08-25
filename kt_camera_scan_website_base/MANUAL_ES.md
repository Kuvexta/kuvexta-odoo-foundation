# Manual — cámara en el sitio web

## Para el administrador

1. Instale `kt_camera_scan_widget`, `website_sale` y este módulo.
2. En Ajustes > ScanFlow Camera, habilite la cámara, el sonido y la cámara
   preferida para cada compañía.
3. Publique los productos que podrán abrir los visitantes y confirme que cada
   variante tenga un código de barras oficial único.
4. Pruebe con un usuario anónimo. Un producto no publicado nunca debe abrirse.

## Para el visitante

Pulse el botón de cámara. Si acepta el permiso, apunte al código; si no tiene
cámara o el permiso falla, escriba el código y pulse **Buscar**.

## Mensajes

- **No se encontró:** el producto no existe, no es vendible o no está publicado.
- **Varios productos:** existen códigos duplicados; un administrador debe
  corregirlos.
- **Deshabilitado:** la compañía apagó el escaneo desde Ajustes.
- **Código no válido:** está vacío, supera 128 caracteres o contiene controles.

El módulo no guarda el código en la sesión del visitante.
## Autoridad documental y mejora continua

- Código y operación de este addon: `Kuvexta/kuvexta-odoo-foundation@19.0`.
- Investigación, diseños, FAQ/PQR, incidentes y lecciones transversales:
  `Kuvexta/kuvexta-odoo-knowledge` mediante `INDEX.yaml` y `CATALOG.yaml`.
- Composición instalable y rollback: bundle exacto de
  `Kuvexta/kuvexta-odoo-integration`.

La copia retenida en Source es evidencia congelada. Toda mejora se propone aquí
y debe actualizar manual, pruebas y comprobante del árbol cuando corresponda.
Los ensayos externos aplicables no se consideran cerrados por una prueba local.
