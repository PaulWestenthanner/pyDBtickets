#!/usr/bin/env python

"""
Setting up program for TrainTicket Extractor.
"""

import pyDBtickets
import setuptools

setuptools.setup(
    name='pyDBtickets',
    description='Functionality to read train tickets issued by Deutsche Bahn (DB)',
    long_description=open('README.md').read(),
    version=pyDBtickets.__version__,
    author=pyDBtickets.__author__,
    author_email=pyDBtickets.__author_email__,
    url='https://github.com/PaulWestenthanner/pyDBtickets',

    packages=[
        'pyDBtickets',
    ],
    test_suite='nose.collector',
    tests_require=['nose', 'mock'],
    entry_points={
        'console_scripts': [
            'apyori-run = apyori:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Freelancers',
        'Intended Audience :: Frequent Travellers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Tools :: Travel Expenses',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)