#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Setup module for the Data-Manager Metadata package.
#
# Mat 2021

from setuptools import setup, find_packages
import os


def get_long_description():
    return open('README.rst').read()


setup(

    name='im-data-manager-metadata',
    version=os.environ.get('GITHUB_REF_SLUG', '0.0.0'),
    author='Tim Dudgeon',
    author_email='tdudgeon@informaticsmatters.com',
    url='https://github.com/InformaticsMatters/data-manager-metadata',
    license='MIT',
    description='A framework for Informatics Matters dataset metadata',
    long_description=get_long_description(),
    keywords='jenkins',
    platforms=['any'],

    # Our modules to package
    packages=find_packages(exclude=['*.test', '*.test.*', 'test.*', 'test']),
    py_modules=['data_manager_metadata'],
    # Minimum requirements to use the metadata.
    # This is different to the requirements.txt file
    install_requires=[
        'PyYAML>=5.3',
        'jsonpickle>=2.0.0',
    ],

    # Supported Python versions
    python_requires='>=3, <4',

    # Project classification:
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    zip_safe=False,

)
