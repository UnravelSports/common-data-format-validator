from setuptools import setup, find_packages
from cdf import __version__ as package_version

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="common-data-format-validator",
    version=package_version,
    author="Joris Bekkers",
    author_email="joris@pysport.org",
    description="A package for validating common data format files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/unravelsports/common-data-format-validator",
    packages=find_packages(),
    package_data={
        "cdf": ["files/schema/*.json", "files/sample/*.json", "files/sample/*.jsonl"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=[
        "jsonlines==4.0.0",
        "jsonschema==4.23.0",
        "jsonschema-specifications==2024.10.1",
        "requests==2.32.3",
    ],
)
