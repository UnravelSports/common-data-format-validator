import builtins
from setuptools import setup, find_packages

builtins.__CDFV_SETUP__ = True
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
        "cdf": [
            "files/v*/schema/*.json",
            "files/v*/sample/*.json",
            "files/v*/sample/*.jsonl",
        ],
    },
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    install_requires=[
        "jsonlines==4.0.0",
        "jsonschema==4.23.0",
        "jsonschema-specifications==2024.10.1",
        "requests==2.32.3",
    ],
    extras_require={
        "dev": [
            # Pinned: the docs CI job byte-compares generated HTML, so a
            # generator upgrade must be a deliberate commit, not a silent bump
            "json-schema-for-humans==1.4.1",
            # Same reasoning: generate_latest_domain.py commits its output, so a
            # generator upgrade rewrites the domain models.
            "datamodel-code-generator==0.55.0",
            # Pinned to match .pre-commit-config.yaml. Black's stable style
            # changes yearly, so an unpinned bump reformats the codebase.
            "black==26.5.1",
            "pytest>=8.4.0",
        ]
    },
)
