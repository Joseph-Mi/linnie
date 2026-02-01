#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name='linnie',
    version='0.0.1',
    description='CM5 MI450 Linnie System Services',
    author='Linnie Team',
    packages=find_packages(),
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'linnie-thermal=linnie.thermal:main',
            'linnie-camera=linnie.camera:main',
        ],
    },
)
