# Manual operativo — KT Camera Scan Widget

## Propósito

Motor técnico reutilizable para escanear códigos de barras y QR con la cámara.
No ejecuta inventario, ventas ni otra lógica de negocio: un módulo consumidor
debe integrar el resultado.

## Instalación y configuración

Instale `kt_camera_scan_widget` desde Apps. En Ajustes revise las opciones de
cámara permitidas por el módulo. El navegador necesita HTTPS —salvo localhost—,
permiso de cámara y un dispositivo compatible. La configuración detallada y las
limitaciones están en `readme/CONFIGURE.rst` y `readme/ROADMAP.rst`.

## Uso y verificación

El widget aparece únicamente en pantallas de addons que lo integren. Autorice la
cámara, enfoque un código y confirme que el consumidor recibe una sola lectura.
Pruebe permiso denegado, ausencia de cámara y cancelación; esos casos deben fallar
de forma controlada. `readme/USAGE.rst` es la guía funcional vigente.

## Soporte

No registre imágenes, códigos sensibles ni credenciales en incidencias. Para una
mejora transversal use la base privada `Kuvexta/kuvexta-odoo-knowledge`; el código
y este manual son autoridad en `Kuvexta/kuvexta-odoo-foundation@19.0`.
## Autoridad documental y mejora continua

- Código y operación de este addon: `Kuvexta/kuvexta-odoo-foundation@19.0`.
- Investigación, diseños, FAQ/PQR, incidentes y lecciones transversales:
  `Kuvexta/kuvexta-odoo-knowledge` mediante `INDEX.yaml` y `CATALOG.yaml`.
- Composición instalable y rollback: bundle exacto de
  `Kuvexta/kuvexta-odoo-integration`.

La copia retenida en Source es evidencia congelada. Toda mejora se propone aquí
y debe actualizar manual, pruebas y comprobante del árbol cuando corresponda.
Los ensayos externos aplicables no se consideran cerrados por una prueba local.
