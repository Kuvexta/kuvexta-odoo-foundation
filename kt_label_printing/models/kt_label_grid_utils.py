# -*- coding: utf-8 -*-
"""Utilidades genéricas y reutilizables para imprimir etiquetas de
producto en cuadrícula — sin ninguna dependencia de QUÉ se dibuja en
cada etiqueta (código de barras, QR, o cualquier otra cosa). Cada
módulo que dibuja su propio contenido (ej. `kt_product_public_qr`)
usa estas funciones en vez de reimplementar la misma lógica."""


def build_label_list(products, copies=1):
    """Arma la lista plana de etiquetas a imprimir, repitiendo cada
    producto la cantidad de copias pedida. Simple a propósito — no
    maneja "varias copias con cantidades distintas por código" como
    el reporte nativo de Odoo (`addons/product/report/product_label_report.py`),
    porque la mayoría de casos de uso reales (QR público, por
    ejemplo) solo necesitan una copia por producto la mayoría de las
    veces."""
    labels = []
    for product in products:
        labels.extend([product] * copies)
    return labels


def compute_page_numbers(label_count, columns, rows):
    """Calcula cuántas páginas hacen falta para acomodar
    `label_count` etiquetas en una cuadrícula de `columns` x `rows`
    por página."""
    if not label_count:
        return 0
    per_page = columns * rows
    if per_page <= 0:
        return 0
    return (label_count - 1) // per_page + 1
