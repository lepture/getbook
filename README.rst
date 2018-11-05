Getbook
=======

Generate ebooks in epub (for iBooks) or mobi (for Kindle) from a collection
of web links and feeds.

.. image:: https://img.shields.io/badge/donate-lepture-ff69b4.svg
   :target: https://lepture.com/donate
   :alt: Donate lepture
.. image:: https://img.shields.io/pypi/v/getbook.svg
   :target: https://pypi.python.org/pypi/getbook/
   :alt: Latest Version
.. image:: https://img.shields.io/pypi/wheel/getbook.svg
   :target: https://pypi.python.org/pypi/getbook/
   :alt: Wheel Status


Installation
------------

Install with pip::

    $ pip install getbook

Note: this program only works on Python3.5+.

You may need to install kindlegen_ to create mobi format books.

.. _kindlegen: https://www.amazon.com/gp/feature.html?ie=UTF8&docId=1000765211

Guide
-----

There are serval ways to generate books.

1. You can generate a book from a feed::

    $ getbook -u http://example.com/feed

2. It is also possible to generate books from a config JSON file::

    $ getbook -f ./book.json

Use ``--format=mobi`` to generate mobi file for kindle::

    $ getbook -f ./book.json --format=mobi

JSON Format
-----------

The required fields in ``book.json`` are:

1. uid: the filename of the book
2. title: book title
3. author: author of the book
4. chapters or sections

Get some examples in https://github.com/lepture/getbook/tree/master/demo

License
-------

This program is licensed under APGL.
