#!/usr/bin/env python
# Copyright 2015 Paul Schwendenman. All Rights Reserved.

from setuptools import setup
import twintrimmer

try:
    README = open('readme.rst', 'r').read()
except OSError:
    README = ''

setup(name='twintrimmer',
      version=twintrimmer.__version__,
      description=twintrimmer.twintrimmer.__doc__.strip(),
      long_description=README,
      author=twintrimmer.__author__,
      author_email=twintrimmer.__email__,
      license=twintrimmer.__license__,
      url='https://github.com/paul-schwendenman/twintrim',
      packages=['twintrimmer'],
      classifiers=['Environment :: Console',
                   'Intended Audience :: Developers',
                   'Intended Audience :: End Users/Desktop',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.4',
                   'Programming Language :: Python :: 3.5',
                   'Programming Language :: Python :: 3 :: Only',
                   'Operating System :: POSIX :: Linux',
                   'Operating System :: MacOS :: MacOS X',
                   'Topic :: Utilities', ],
      entry_points=
      {'console_scripts': ['twintrim = twintrimmer:main'], },
      test_suite='tests', )
