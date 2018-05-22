#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Python ctrl.systemd
"""

from setuptools import setup


install_requires = [
    'ctrl.config',
    'ctrl.core',
    'ctrl.command',
    'pyyaml',
    'systemd-python']
extras_require = {}
extras_require['test'] = [
    "pytest",
    "pytest-mock",
    "coverage",
    "pytest-coverage",
    "codecov",
    "flake8"],

setup(
    name='ctrl.systemd',
    version='0.0.1',
    description='ctrl.systemd',
    long_description="ctrl.systemd",
    url='https://github.com/phlax/ctrl.systemd',
    author='Ryan Northey',
    author_email='ryan@synca.io',
    license='GPL3',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        ('License :: OSI Approved :: '
         'GNU General Public License v3 or later (GPLv3+)'),
        'Programming Language :: Python :: 3.5',
    ],
    keywords='python ctrl systemd',
    install_requires=install_requires,
    extras_require=extras_require,
    packages=['ctrl.systemd'],
    include_package_data=True)
