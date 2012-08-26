#!/usr/bin/env python
import os
import die

try:
    from distutils.core import setup
except ImportError:
    from setuptools import setup


setup(
    name='die',
    packages=['die', ],
    version=die.__version__,
    author=die.__author__,
    author_email=die.__email__,
    url='https://github.com/njharman/die',
    description='''Library for simulating dice, dice rolls, and stats on dice.''',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst'), 'r').read(),
    license='GPL - GNU Public License',
    platforms=['POSIX', 'Windows'],
    classifiers=[
        'Topic :: Games/Entertainment',
        'Topic :: Games/Entertainment :: Role-Playing',
        'Topic :: Games/Entertainment :: Board Games',
        'Topic :: Software Development :: Libraries',
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        ],
    )
