#!/usr/bin/env python

"""
Setting up program for Apyori.
"""

import TrainTickets
import setuptools

setuptools.setup(
    name='pyDBtickets',
    description='Functionality to read train tickets issued by Deutsche Bahn (DB)',
    long_description=open('README.md').read(),
    version=TrainTickets.__version__,
    author=TrainTickets.__author__,
    author_email=TrainTickets.__author_email__,
    url='https://github.com/ymoch/apyori',
    py_modules=['apyori'],
    test_suite='nose.collector',
    tests_require=['nose', 'mock'],
    entry_points={
        'console_scripts': [
            'apyori-run = apyori:main',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)