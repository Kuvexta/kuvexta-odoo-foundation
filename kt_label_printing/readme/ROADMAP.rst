- Soporte para generar etiquetas en formato ZPL (impresión térmica
  directa) — diseñado, sin construir. Ver
  ``DISENO_IMPRESION_MASIVA.md`` dentro de ``kt_product_public_qr``.
- ``kt_product_multi_barcode`` ya depende de este módulo y reutiliza
  ``compute_page_numbers()`` (Fase 0, 15/08/2026 — ver
  ``disenos_completos/kt_label_printing/DISENO_ARQUITECTURA_ETIQUETAS.md``).
  **Pendiente solo si surge la
  necesidad real** (evaluado y descartado por ahora, no es
  sobre-ingeniería especulativa): que ese módulo también use
  ``kt.label.size`` (tamaño de etiqueta configurable) y el mixin de
  exportación PNG/ZIP para los códigos alternos — el patrón exacto a
  copiar ya existe en ``kt_product_public_qr/models/
  product_label_layout.py``.
