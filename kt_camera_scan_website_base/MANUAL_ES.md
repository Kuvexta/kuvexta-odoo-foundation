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
