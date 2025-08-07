#!/usr/bin/env python3
"""
Setup script for neuroloopy package.
"""

from setuptools import setup, find_packages
import os

# Read long description from README if available
long_description = "Real-time fMRI neurofeedback processing package"
if os.path.exists("README.md"):
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()

setup(
    name="neuroloopy",
    version="0.1.0",
    author="neuroloopy development team",
    description="Real-time fMRI neurofeedback processing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Scientific/Engineering :: Image Processing",
    ],
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.19.0",
        "scipy>=1.5.0",
        "nibabel>=3.0.0",
        "watchdog>=2.0.0",
        "requests>=2.25.0",
        "PyYAML>=5.4.0",
        "dill>=0.3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.10",
            "black>=21.0",
            "flake8>=3.8",
        ]
    },
    entry_points={
        "console_scripts": [
            "neuroloopy=neuroloopy.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "neuroloopy": [
            "config/*.yaml",
            "dashboard/*",
        ],
    },
)
