#!/usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import setup

version = '0.1'
homepage = 'https://doocer.com/'


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
    description='TODO',
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    long_description=fread('README.rst'),
    license='GNU AGPLv3+',
    install_requires=install_requirements,
    project_urls={},
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
