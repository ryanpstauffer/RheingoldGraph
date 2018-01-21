#!/usr/bin/env python

import os
from glob import glob

from setuptools import find_packages
from setuptools import setup

setup(
    name='rheingoldgraph',
    version='0.0.1',
    license='Apache License 2.0',
    description='A Music Graph',
    author='Ryan Stauffer',
    author_email='ryan.p.stauffer@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[os.path.splitext(os.path.basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Languaged :: Python :: 3'
    ],
    install_requires=[
        'gremlinpython==3.3.1',
        'mido==1.2.8'
    ]
)
