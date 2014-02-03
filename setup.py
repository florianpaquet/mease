#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

requires = [
    'autobahn==0.7.4',
    'Twisted==13.2.0'
]

setup(
    name='mease',
    version='0.2.0',
    description="Mease: Twisted/Autobahn websocket server with an easy callback registry",
    url="https://github.com/florianpaquet/mease",
    author="Florian PAQUET",
    author_email="contact@florianpaquet.com",
    long_description=read('README.rst'),
    license='MIT',
    test_suite='mease.tests',
    packages=[
        'mease',
        'mease.backends',
    ],
    install_requires=requires,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ])
