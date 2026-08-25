Expone un único botón flotante en la web pública. El motor compartido intenta
primero ``BarcodeDetector`` del navegador y después el respaldo local
ZBar/WASM de ``kt_camera_scan_widget``. Si ninguno está disponible, la entrada
manual permanece operativa.

El servidor busca exclusivamente el campo oficial ``barcode`` y vuelve a
aplicar el dominio público nativo de Website Sale. Una coincidencia oculta,
no vendible o ambigua no produce una URL.
