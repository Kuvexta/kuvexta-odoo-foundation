Ir a **Ajustes generales > ScanFlow Camera** y configurar:

``kt_camera_scan_enabled``
    Si el botón de "escanear con cámara" aparece en los documentos que lo
    soportan. Desactivado, esos documentos solo ofrecen el lector físico.

``kt_camera_scan_beep_enabled``
    Si el sonido de confirmación al detectar un código está activo.
    Desactivar en ambientes de oficina donde el sonido no es deseable.

``kt_camera_scan_default_facing``
    Qué cámara se abre por defecto al iniciar el escaneo: trasera
    (recomendado, mejor para escanear objetos) o frontal.

Este módulo no depende de configuración por documento — cada módulo que lo
consume (por ejemplo ``kt_scanflow_documents``) decide en qué documentos
ofrecer la opción de cámara.
