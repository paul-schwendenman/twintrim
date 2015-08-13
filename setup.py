#!/usr/bin/env python
# Copyright 2015 Paul Schwendenman. All Rights Reserved.

from setuptools import setup

try:
    readme = open('readme.rst', 'r').read()
except:
    readme = ''

setup(name='twintrimmer',
      version='0.7a',
      description='tool for removing duplicate files',
      long_description=readme,
      author='Paul Schwendenman',
      author_email='schwendenman.paul+twintrim@gmail.com',
      license='MIT',
      url='https://github.com/paul-schwendenman/twintrim',
      packages=['twintrimmer'],
      classifiers=['Environment :: Console',
                   'Intended Audience :: Developers',
                   'Intended Audience :: End Users/Desktop',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.4',
                   'Operating System :: POSIX :: Linux',
                   'Topic :: Utilities', ],
      entry_points=
      {'console_scripts': ['twintrim = twintrimmer:run.terminal'], }, )
