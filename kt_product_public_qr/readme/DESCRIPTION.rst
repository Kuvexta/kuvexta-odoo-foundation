This module publishes a **public, no-login web page** for each
product (``product.template``), reachable via a random, non-guessable
access token, and a matching printable QR code ("grouping QR") that
links to it.

The page shows:

* Product name and image.
* The official barcode.
* The official barcode for each variant.

Alternate codes are an optional Professional extension supplied by
``kt_product_public_qr_multi_barcode``. The Foundation module has no hard or
soft dependency on that model and never exposes supplier, channel or stock.

**Multi-website support.** If your Odoo instance serves several
domains from the same database (Odoo's native multi-website feature),
each product can be assigned to a specific ``website.website``. The
generated link then uses that website's own domain, and a visitor
reaching the page through a different domain is automatically
redirected to the correct one.
