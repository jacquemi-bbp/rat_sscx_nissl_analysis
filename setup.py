#!/usr/bin/env python
""" Distribution configuration for qupath_processing"""
import importlib
from setuptools import setup
from setuptools import find_packages

spec = importlib.util.spec_from_file_location("qupath_processing.version", "qupath_processing/version.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
VERSION = module.VERSION

with open('requirements.txt') as f:
    requirements = f.readlines()

setup(
    classifiers=[
        'Programming Language :: Python :: 3.8',
    ],
    description='qupath_processing=Process files export from QuPath to create rat sscx nissl cells densities',
    author='Jean Jacquemier',
    version=VERSION,
    install_requires=requirements,
    packages=find_packages(),
    name='qupath_processing',
    entry_points={
        'console_scripts': ['pyqupath_processing=qupath_processing.app.__main__:process',
                            'pyqupath_batch_processing=qupath_processing.app.__main__:batch',
                            ]
    }
)
