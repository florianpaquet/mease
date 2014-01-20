#!/usr/bin/env python
import os
import sys
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

requires = [
    'tornado>=3.2',
]

if sys.version_info[0] == 2:
    requires.append('futures')

setup(
    name='mease',
    version='0.1.0',
    description="Mease: Tornado websocket server with an easy callback registry",
    url="https://github.com/florianpaquet/mease",
    author="Florian PAQUET",
    author_email="contact@florianpaquet.com",
    long_description=read('README.rst'),
    license='MIT',
    packages=[
        'mease',
        'mease.backends',
    ],
    install_requires=requires,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ])
