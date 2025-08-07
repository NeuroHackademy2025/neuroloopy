from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="neuroloopy",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Real-time fMRI processing package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/neuroloopy",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "neuroloopy=neuroloopy.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "neuroloopy": ["config/*.yaml"],
    },
)