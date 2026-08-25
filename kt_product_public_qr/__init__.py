import uuid

from . import controllers, models, report


def _kt_assign_unique_public_tokens(env):
    """Corrección real (04/08/2026): confirmado con una prueba real
    que todos los productos que YA EXISTÍAN antes de instalar este
    módulo terminaban con el MISMO `kt_public_access_token` — Odoo, al
    agregar una columna nueva con un valor por defecto CALCULADO
    (`default=lambda self: uuid.uuid4().hex`) a una tabla con
    registros ya existentes, calcula ese valor **una sola vez** y lo
    aplica igual a todas las filas existentes (una optimización
    interna del propio ORM, pensada para tablas grandes) — no llama
    la función una vez POR REGISTRO como sí hace en una creación
    normal después de instalado.

    Este `post_init_hook` corre una sola vez, justo después de
    instalar el módulo, y le asigna a cada producto YA EXISTENTE un
    token realmente único — sin esto, todos los productos antiguos
    comparten el mismo enlace público, mostrando siempre la
    información del mismo producto sin importar cuál se consulte."""
    products = env["product.template"].search([])
    for product in products:
        product.kt_public_access_token = uuid.uuid4().hex
