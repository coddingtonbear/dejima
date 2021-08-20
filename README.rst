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

.. |version| image:: https://img.shields.io/pypi/v/boox-annotations-to-anki.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/boox-annotations-to-anki

.. |wheel| image:: https://img.shields.io/pypi/wheel/boox-annotations-to-anki.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/boox-annotations-to-anki

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/boox-annotations-to-anki.svg
    :alt: Supported versions
    :target: https://pypi.org/project/boox-annotations-to-anki

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/boox-annotations-to-anki.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/boox-annotations-to-anki

.. |commits-since| image:: https://img.shields.io/github/commits-since/coddingtonbear/boox-annotations-to-anki/v0.1.1.svg
    :alt: Commits since latest release
    :target: https://github.com/coddingtonbear/boox-annotations-to-anki/compare/v0.1.1...master

.. end-badges

Create cards in Anki from your Onyx Boox annotations.

* Free software: MIT license

Installation
============

::

    pip install boox-annotations-to-anki

You can also install the in-development version with::

    pip install https://github.com/coddingtonbear/boox-annotations-to-anki/archive/master.zip


Requirements
============

- AnkiConnect: https://ankiweb.net/shared/info/2055492159

Documentation
=============

You can import your cards into Anki by running::


    boox-annotations-to-anki MY_DECK_NAME --input=/path/to/boox/annotations.txt
