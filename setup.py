#!/usr/bin/env python3
"""
Setup script for keyboard-checker

Copyright (C) 2025

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from setuptools import setup

setup(
    name='keyboard-checker',
    version='1.0.0',
    description='Graphical keyboard testing utility with typing test',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Jeff Lane',
    author_email='jeffrey.lane@canonical.com',
    url='https://github.com/bladernr/keyboard-checker',
    license='GPL-3.0+',
    py_modules=['keyboard_checker', 'text_samples'],
    scripts=['keyboard_checker.py'],
    python_requires='>=3.8',
    install_requires=[
        'PyQt6>=6.0.0',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Utilities',
    ],
)
