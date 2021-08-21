========================
Boox Annotations to Anki
========================

.. start-badges

.. list-table::
    :stub-columns: 1

    * - tests
      - |
        |
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|

.. |version| image:: https://img.shields.io/pypi/v/dejima.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/dejima

.. |wheel| image:: https://img.shields.io/pypi/wheel/dejima.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/dejima

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/dejima.svg
    :alt: Supported versions
    :target: https://pypi.org/project/dejima

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/dejima.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/dejima

.. |commits-since| image:: https://img.shields.io/github/commits-since/coddingtonbear/dejima/v1.0.1.svg
    :alt: Commits since latest release
    :target: https://github.com/coddingtonbear/dejima/compare/v1.0.1...master

.. end-badges

Create cards in Anki by importing data in a variety of formats.

* Free software: MIT license

Installation
============

::

    pip install dejima

You can also install the in-development version with::

    pip install https://github.com/coddingtonbear/dejima/archive/master.zip


Requirements
============

- AnkiConnect: https://ankiweb.net/shared/info/2055492159

Supported Sources
=================

- ``boox``: Allows you to import reading annotations exported from an Onyx Boox e-reader or notepad.

Documentation
=============

You can import your cards into Anki by running::

    dejima import MY_DECK_NAME SOURCE_NAME --input=/path/to/some/file.txt
