import builtins
import pathlib
import re
from setuptools import setup, find_packages

builtins.__CDFV_SETUP__ = True
from cdf import __version__ as package_version

# Read the CDF schema version from the source rather than importing it. The
# __CDFV_SETUP__ flag above deliberately stops cdf/__init__.py pulling in the
# validators, so `from cdf import VERSION` is not available here, and importing
# cdf.validators directly would require jsonschema at build time.
schema_version = re.search(
    r'^VERSION = "([^"]+)"',
    pathlib.Path("cdf/validators/__init__.py").read_text(encoding="utf-8"),
    re.MULTILINE,
).group(1)

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="common-data-format-validator",
    version=package_version,
    author="Joris Bekkers",
    author_email="joris@pysport.org",
    description=(
        "Validates football match data against the Common Data Format "
        f"(currently CDF v{schema_version})"
    ),
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
