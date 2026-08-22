No expone ninguna pantalla ni menú — se usa solo desde código de otro
módulo::

    from odoo.addons.kt_marketplace_core_utils.hooks_core_jump import (
        apply_generic_core_jump,
    )
    from odoo.addons.kt_marketplace_core_utils.hooks_stale_views import (
        purge_stale_extracted_core_views,
    )

Ambas funciones son idempotentes: correrlas de nuevo sobre una base
que ya está al día no hace nada (ni rompe nada).
