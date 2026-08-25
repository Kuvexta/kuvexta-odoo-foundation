=====================
KT Product Public QR
=====================

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-LGPL--3-blue.png
    :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
    :alt: License: LGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-Kuvexta%2Fodoo--community--tools-lightgray.png?logo=github
    :target: https://github.com/Kuvexta/odoo-community-tools/tree/19.0/kt_product_public_qr
    :alt: Kuvexta/odoo-community-tools

|badge1| |badge2| |badge3|

Public, no-login product info page reachable via a printable grouping
QR code. Foundation module depending only on Odoo and
``kt_label_printing``.

**Table of contents**

.. contents::
   :local:

Description
===========

This module publishes a **public, no-login web page** for each
product (``product.template``), reachable via a random, non-guessable
access token, and a matching printable QR code ("grouping QR") that
links to it.

The page shows:

* Product name and image.
* The official barcode.
* The official barcode for each variant.

The optional Professional module ``kt_product_public_qr_multi_barcode`` adds
alternate codes. This Foundation tree never imports or queries Professional
models and never exposes supplier, channel or on-hand quantity.

**Multi-website support.** If your Odoo instance serves several
domains from the same database (Odoo's native multi-website feature),
each product can be assigned to a specific ``website.website``. The
generated link then uses that website's own domain, and a visitor
reaching the page through a different domain is automatically
redirected to the correct one.

Configuration
=============

No configuration is required for a single-domain installation.

If your database serves several domains (Odoo's multi-website
feature, ``Settings → General Settings → activate "Multi-website"``),
open a product's form, tab **"QR público"**, and set **"Sitio web de
la página pública"** to the ``website.website`` record that should own
that product's public link. Leave it empty to use the instance's
generic/default domain.

Usage
=====

From any product's form (``Inventory → Products → Products``):

1. Click the **"Página pública"** smart button to preview the public
   page in a new tab before printing anything.
2. Use ``Print → Etiqueta QR de producto (agrupador)`` to generate a
   printable label with the QR code linking to that page.
3. Anyone scanning that QR (staff without an Odoo account, or a
   customer) sees the product's basic info without logging in.

To invalidate a shared link, use **Regenerate public link** in the product's
``Public QR`` tab and reprint any physical label that used the old token.

Roadmap
=======

* Execute the 19.0.2.0.0 upgrade and QR/device smoke in staging before each
  production promotion.
* ZPL/vendor printing is deliberately outside this module; see the authorized
  Vendor Adapter documentation.

More documentation
===================

* ``docs/ESTADO.md`` — current state and historical production evidence.
* ``docs/FAQ.md`` — frequently asked questions (in Spanish).

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/Kuvexta/odoo-community-tools/issues>`_.

Credits
=======

Authors
-------

* Kuvexta

Contributors
------------

* Kuvexta <https://github.com/Kuvexta>

Maintainers
-----------

This module is maintained by Kuvexta.
