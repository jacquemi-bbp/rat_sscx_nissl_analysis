#!/usr/bin/env python
""" Distribution configuration for qpath_processing"""
import importlib
from setuptools import setup
from setuptools import find_packages

spec = importlib.util.spec_from_file_location("qpath_processing.version", "qpath_processing/version.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
VERSION = module.VERSION


setup(
    classifiers=[
        'Programming Language :: Python :: 3.8',
    ],
    description='qpath_processing=Process files export from QuPath to create rat sscx nissl cells densities',
    author='Jean Jacquemier',
    version=VERSION,
    install_requires=['matplotlib>=3.3.2',
                      'numpy>=1.19.5',
                      'pandas>=1.3.1',
                      'openpyxl==3.0.7',
                      'geojson==2.5.0',
                      'shapely==1.7.0',
                      'Click>=7.1.2'
                      ],
    packages=find_packages(),
    name='qpath_processing',
    entry_points={
        'console_scripts': ['pyqupath_processing=qpath_processing.app.__main__:process']
    }
)
