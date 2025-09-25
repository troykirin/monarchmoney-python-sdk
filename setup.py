import os

from setuptools import setup

install_requires = open("requirements.txt", "r").read().split("\n")

setup(
    name="monarchmoney",
    description="Monarch Money API for Python",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/NabiaTech/monarchmoney-python-sdk",
    author="NabiaTech",
    author_email="contact@nabiatech.com",
    license="MIT",
    keywords="monarch money, financial, money, personal finance",
    install_requires=install_requires,
    packages=["monarchmoney"],
    include_package_data=True,
    zip_safe=False,
    platforms="any",
    entry_points={
        "console_scripts": [
            "monarchmoney=monarchmoney.cli:cli_main",
        ],
    },
    scripts=["bin/monarchmoney"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Topic :: Office/Business :: Financial",
        "Topic :: Office/Business :: Financial :: Investment",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)
