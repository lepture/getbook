#!/usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import setup
from getbook import __version__ as version
from getbook import __homepage__ as homepage


def fread(filename):
    with open(filename) as f:
        return f.read()


install_requirements = [
    'beautifulsoup4',
    'Jinja2',
    'lxml',
    'Pillow',
    'python-dateutil',
    'requests',
]


setup(
    name='getbook',
    version=version,
    author='Hsiaoming Yang',
    author_email='me@lepture.com',
    url=homepage,
    packages=[
        'getbook',
        'getbook.core',
        'getbook.sites',
        'getbook.ebook',
    ],
    entry_points={
        'console_scripts': [
            'getbook = getbook.cli:main'
        ],
    },
    description='Generate e-books in EPUB or MOBI from websites',
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    long_description=fread('README.rst'),
    license='GNU AGPLv3+',
    install_requires=install_requirements,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
