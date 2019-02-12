#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Setup file for ecas_b2share.
    Use setup.cfg to configure your project.


"""
import sys

from pkg_resources import require, VersionConflict
from setuptools import setup, find_packages

try:
    require('setuptools>=38.3')
except VersionConflict:
    print("Error: version of setuptools is too old (<38.3)!")
    sys.exit(1)

long_description = (
    open('README.rst').read() + '\n' + open('AUTHORS.rst').read() + '\n' + open('CHANGELOG.rst').read()
)
version = __import__('ecasb2share').__version__
description = 'ecasb2share provides a python library to interact with B2SHARE REST API.'
reqs = [line.strip() for line in open('requirements.txt')]

classifiers=[
          'Development Status :: 3 - Alpha',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: Software Development :: Bug Tracking',
          ],

setup(name='ecasb2share',
      version=version,
      description=description,
      long_description=long_description,
      classifiers=classifiers,
      keywords='ecas rest python eosc-hub b2share',
      author='Sofiane Bendoukha',
      author_email="bendoukha@dkrz.de",
      url='https://github.com/bird-house/birdy',
      license="mit",
      packages=find_packages(),
      include_package_data=True,
      install_requires=reqs,

      )

