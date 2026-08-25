=============================
KT Camera Scan - Website Base
=============================

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
   :target: https://odoo-community.org/page/development-status
   :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-LGPL--3-blue.png
   :target: https://www.gnu.org/licenses/lgpl-3.0.html
   :alt: License: LGPL-3

|badge1| |badge2|

Capa Foundation que permite escanear con cámara o escribir un código oficial
en el sitio público y abrir únicamente un producto publicado y vendible.

No depende de multi-barcode, no escribe sesión y no reutiliza el controlador
histórico. Los códigos alternos se agregan mediante el bridge Professional
``kt_camera_scan_website_multi_barcode``.

**Table of contents**

.. contents::
   :local:

Description
===========

See ``readme/DESCRIPTION.rst``.

Configuration
=============

See ``readme/CONFIGURE.rst``.

Usage
=====

See ``readme/USAGE.rst`` and ``MANUAL_ES.md``.

Known issues / Roadmap
======================

See ``readme/ROADMAP.rst``.

Credits
-------

Authors
-------

* Kuvexta
Documentation authority and support
===================================

* Addon code and operational documentation: `Kuvexta/kuvexta-odoo-foundation@19.0`.
* Spanish operator manual: `MANUAL_ES.md`.
* Cross-cutting designs, FAQ/PQR and lessons: private
  `Kuvexta/kuvexta-odoo-knowledge`; start with `INDEX.yaml` and select
  only the applicable document from `CATALOG.yaml`.
* Deploy only an exact bundle locked by `Kuvexta/kuvexta-odoo-integration`.

The retained copy in `odoo-community-tools` is migration evidence, not a
second development branch. External staging, backup-restore and authorized
provider/device smokes remain separate release gates when applicable.
