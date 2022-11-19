#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages
from pyqa import __version__, __author__, __email__

with open("README.md") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = [
    "Click>=7.0",
    "rich>=12.6.0",
    "textual>=0.4.0",
    "pyfiglet>=0.8.post1",
]

test_requirements = [
    "pytest>=3",
]

setup(
    author=__author__,
    author_email=__email__,
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="Python console appliction that searches the internet for asnwers to coding problems",
    entry_points={
        "console_scripts": [
            "pyqa=pyqa.cli:main",
        ],
    },
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description=readme + "\n\n" + history,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords="pyqa",
    name="pyqa-y8l",
    packages=find_packages(include=["pyqa", "pyqa.*"]),
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/yusufadell/pyqa",
    version=__version__,
    zip_safe=False,
)
