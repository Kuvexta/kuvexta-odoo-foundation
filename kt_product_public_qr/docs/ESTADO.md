# Estado del desarrollo — kt_product_public_qr

**Última actualización: 24/08/2026 — versión 19.0.2.0.0 separada como
Foundation neutral; CI reproducible pendiente de esta rama.**

## Estado actual

- Token, página, imagen, variantes, PDF y PNG permanecen LGPL-3.
- Se retiró la dependencia dura de `kt_product_multi_barcode`.
- Los códigos alternos ahora pertenecen al bridge Professional
  `kt_product_public_qr_multi_barcode`.
- La impresión Webkul nueva pertenece a `kt_webkul_public_qr_print`, OPL-1 y
  `service_only`; el histórico `kt_qr_webkul_print` no se migró ni relicenció.
- Quedan como gates externos el upgrade en staging y el smoke de dispositivo;
  no invalidan las pruebas reproducibles de código y dependencias.

> **Nota:** las secciones de más abajo se dejan tal cual se escribieron
> en su momento (03-04/08/2026), como registro histórico real de cómo
> se fue resolviendo — incluida una sección que en su momento decía
> "todavía no ha corrido en un servidor Odoo real" y quedó obsoleta
> apenas unos días después, cuando sí se confirmó. Para el estado
> ACTUAL real, ver únicamente esta sección de arriba y la tabla de
> `README.md` (raíz del repo), no las secciones de abajo.

## ✅ Resuelto — la causa real, y por qué la investigación anterior no la encontró

El bloqueo documentado el 01/08/2026 (`'website.website' in
env.registry.models` → `False`) **nunca fue un problema del
servidor**. Fue un error real en nuestro propio código: el modelo de
sitios web de Odoo se llama simplemente **`website`**, no
`website.website` — un nombre que asumimos sin verificar contra el
código fuente real (el mismo tipo de error que se repitió varias
veces más durante el desarrollo de `kt_product_multi_barcode` los
días siguientes: `stock.quant.package` → en realidad `stock.package`
en Odoo 19, `product_uom` con y sin sufijo `_id` según el modelo,
etc. — una lección recurrente de todo este proyecto).

**Confirmado el 03/08/2026, verificado contra el código fuente real:**
```python
# addons/website/models/website.py
class Website(models.Model):
    _name = 'website'   # <- NO 'website.website'
```

Y confirmado en el propio servidor, por consola:
```python
>>> 'website' in env.registry.models
True
>>> env['website'].search([]).mapped('name')
['NEXO FERRETERO', 'Grupo Comercializador SuBienes S.A.S.']
```

**Corrección aplicada:** el campo `kt_public_website_id`
(`models/product_template.py`) cambió de
`fields.Many2one('website.website', ...)` a
`fields.Many2one('website', ...)`. Se revisó el resto del módulo
(controlador, vistas, reporte) y no había ninguna otra referencia al
nombre incorrecto — el campo `domain` usado en el controlador
(`assigned_website.domain`) también se verificó contra el código
fuente real y es correcto tal cual estaba.

## ✅ Confirmado funcionando en producción (03/08/2026)

Instalado en `gc` (`srv820446`), versión `19.0.1.0.1`. Confirmado con
una prueba real:

- Instalación limpia, sin errores (`ir_module_module.state = 'installed'`).
- Los 3 campos nuevos (`kt_public_access_token`, `kt_public_qr_url`,
  `kt_public_website_id`) existen correctamente en `product.template`.
- El enlace público se genera correctamente
  (`https://gc.subienes.com/producto/<token>`).
- La página pública **carga sin pedir sesión**, probado en ventana de
  incógnito.

## ✅ Impresión masiva, ZPL y exportación PNG — ya construidos y confirmados (04/08/2026)

Lo que esta sección originalmente listaba como "pendiente de
construir" (impresión masiva en cuadrícula, etiquetas ZPL para
impresión térmica directa, exportación masiva de imágenes PNG, y
tamaños de etiqueta configurables) **ya está construido y confirmado
funcionando con una prueba real** — ver `docs/DISENO_IMPRESION_MASIVA.md`
para el detalle técnico completo de cada punto, y el módulo puente
el adapter histórico `kt_qr_webkul_print`. Desde ADR-10 ese addon se conserva
solo como evidencia LGPL-3; el reemplazo limpio es
`kt_webkul_public_qr_print` y requiere Webkul licenciado, no incluido.

## Lo que sigue pendiente — ahora sí, instalación real

Con la causa raíz corregida, el módulo está listo para el primer
intento real de instalación (nunca se ha probado en un servidor
Odoo, solo validado estáticamente):

1. **Probar en `kt_test_dev` primero, no en `gc` directamente.**
2. Confirmar que se instala sin errores.
3. Confirmar que el botón "Página pública" abre la URL correctamente.
4. Confirmar que la página pública carga sin necesidad de sesión.
5. Confirmar que la etiqueta QR se imprime y escanea correctamente.
6. Solo después de esas pruebas, considerar el módulo "estable" y
   quitar esta advertencia del README.

## Qué SÍ está listo (código, corregido, pendiente de primera prueba en vivo)

- Modelo (`models/product_template.py`): token único, cómputo de URL
  pública, campo de sitio web para multi-dominio (ya corregido),
  validación de unicidad del token.
- Controlador (`controllers/main.py`): ruta pública, redirección
  automática si el dominio no coincide con el sitio asignado del
  producto.
- Vista pública (`views/product_public_info_templates.xml`): página neutral
  con nombre, imagen y código oficial por variante; ofrece puntos de extensión
  para capas superiores.
- Vista de administración (`views/product_views.xml`): botón "Página
  pública" y campos en la ficha de producto.
- Reporte de etiqueta (`report/product_public_qr_label_report.xml`):
  imprime el QR usando el widget nativo de Odoo.

Todo esto pasó validación estática (sintaxis Python, XML bien
formado) y ahora también la corrección del bug real de nombre de
modelo — pero **todavía no ha corrido en un servidor Odoo real**.
