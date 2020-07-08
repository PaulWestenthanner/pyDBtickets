#!/usr/bin/env python

"""
Setting up program for TrainTicket Extractor.
"""

import PyDBtickets
import setuptools

setuptools.setup(
    name='PyDBtickets',
    description='Functionality to read train tickets issued by Deutsche Bahn (DB)',
    long_description=open('README.md').read(),
    version=PyDBtickets.__version__,
    author=PyDBtickets.__author__,
    author_email=PyDBtickets.__author_email__,
    url='https://github.com/PaulWestenthanner/PyDBtickets',

    packages=[
        'PyDBtickets',
    ],
    install_requires=[
        'pyexcel==0.6.2',
        'textract==1.6.1',
        'pyexcel-ods3==0.5.3',
        'pandas==1.0.5',
        'xlrd==1.1.0'
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
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Tools :: Travel Expenses',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)