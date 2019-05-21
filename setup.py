#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Setup file for ecas_b2share.
    Use setup.cfg to configure your project.


"""
import sys

from pkg_resources import require, VersionConflict
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class NoseTestCommand(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # Run nose ensuring that argv simulates running nosetests directly
        import nose
        nose.run_exit(argv=['nosetests'])


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

setup(name='ecasb2share',
      version=version,
      description=description,
      long_description=long_description,
      long_description_content_type='text/x-rst',
      tests_require=[
          'nose',
          'mock',
          'coverage'
      ],
      cmdclass={'test': NoseTestCommand},
      classifiers=[
          'Development Status :: 4 - Beta',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3',
          'Topic :: Software Development :: Bug Tracking',
      ],
      keywords='ecas rest python eosc-hub b2share',
      author='Sofiane Bendoukha',
      url='https://github.com/SofianeB/ECAS-B2SHARE',
      license="mit",
      packages=find_packages(),
      include_package_data=True,
      install_requires=reqs,
      test_suite='nose.collector',
      py_modules=['ecasb2share_cli'],
      entry_points='''
          [console_scripts]
          ecasb2share_cli=ecasb2share_cli:main
      ''',


      )
