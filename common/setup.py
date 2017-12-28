#!/usr/bin/env python
# -*- coding:utf-8 -*-

from setuptools import find_packages, setup

setup(
    name='pfc-analysis-tools',
    version='0.0',
    description="""
    common script for:
        - data preprocessing
        - growth prediction
        - other frequently used tools
    """,
    packages = find_packages(),
    include_package_data=True,
    install_requires=[
        'couchdb',
        'matplotlib',
        'numpy',
        'opencv-python',
        'pandas',
    ]
)