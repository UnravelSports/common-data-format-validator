import pytest
import os
from pathlib import Path
import sys
import json
import re

# Get the project root directory
project_root = Path(__file__).parent.parent

# Add the project root to the Python path
sys.path.insert(0, str(project_root))

from cdf import (
    TrackingSchemaValidator,
    MetaSchemaValidator,
    EventSchemaValidator,
    MatchSchemaValidator,
    SkeletalSchemaValidator,
    VERSION,
)

SAMPLE_PATH = Path("cdf", "files")


# Setup fixtures for each validator
@pytest.fixture
def tracking_validator():
    return TrackingSchemaValidator()


@pytest.fixture
def meta_validator():
    return MetaSchemaValidator()


@pytest.fixture
def event_validator():
    return EventSchemaValidator()


@pytest.fixture
def match_validator():
    return MatchSchemaValidator()


@pytest.fixture
def skeletal_validator():
    return SkeletalSchemaValidator()


@pytest.fixture
def index_html_path():
    """Return the path to the index.html file."""
    return Path("docs/index.html")


# Sample file paths
@pytest.fixture
def sample_files():
    return {
        "tracking": SAMPLE_PATH / f"v{VERSION}" / "sample" / f"tracking.jsonl",
        "meta": SAMPLE_PATH / f"v{VERSION}" / "sample" / f"meta.json",
        "event": SAMPLE_PATH / f"v{VERSION}" / "sample" / f"event.jsonl",
        "match": SAMPLE_PATH / f"v{VERSION}" / "sample" / f"match.json",
        "skeletal": SAMPLE_PATH / f"v{VERSION}" / "sample" / f"skeletal.jsonl",
    }


@pytest.fixture
def schema_files():
    return {
        "tracking": SAMPLE_PATH / f"v{VERSION}" / "schema" / f"tracking.json",
        "meta": SAMPLE_PATH / f"v{VERSION}" / "schema" / f"meta.json",
        "event": SAMPLE_PATH / f"v{VERSION}" / "schema" / f"event.json",
        "match": SAMPLE_PATH / f"v{VERSION}" / "schema" / f"match.json",
        "skeletal": SAMPLE_PATH / f"v{VERSION}" / "schema" / f"skeletal.json",
    }


# Tests for each validator
def test_tracking_schema_validation(tracking_validator, sample_files):
    """Test that tracking schema validation runs without errors."""
    result = tracking_validator.validate_schema(sample=sample_files["tracking"])
    # If no exception is raised, validation succeeded
    assert (
        result is None or result is True
    )  # Depending on what the method returns on success


def test_meta_schema_validation(meta_validator, sample_files):
    """Test that meta schema validation runs without errors."""
    result = meta_validator.validate_schema(sample=sample_files["meta"])
    assert result is None or result is True


def test_skeleta_schema_validation(skeletal_validator, sample_files):
    """Test that skeletal schema validation runs without errors."""
    result = skeletal_validator.validate_schema(sample=sample_files["skeletal"])
    assert result is None or result is True


def test_event_schema_validation(event_validator, sample_files):
    """Test that event schema validation runs without errors."""
    result = event_validator.validate_schema(sample=sample_files["event"])
    assert result is None or result is True


def test_match_schema_validation(match_validator, sample_files):
    """Test that match schema validation runs without errors."""
    result = match_validator.validate_schema(sample=sample_files["match"])
    assert result is None or result is True


# Optional: Test for validation failure with invalid data
def test_tracking_schema_validation_failure(tracking_validator, tmp_path):
    """Test that tracking schema validation fails with invalid data."""
    # Create an invalid sample file
    invalid_file = tmp_path / "invalid_tracking.jsonl"
    with open(invalid_file, "w") as f:
        f.write('{"invalid_key": "invalid_value"}\n')

    # Expect validation to fail
    with pytest.raises(Exception):  # Replace with specific exception if known
        tracking_validator.validate_schema(sample=str(invalid_file))


def test_all_domain_files_have_correct_version():
    """Ensure all generated domain files match the current VERSION."""
    domain_dir = Path("cdf/domain/latest")
    expected_header = f"# Auto-generated from JSON Schema v{VERSION}"

    files_to_check = [f for f in domain_dir.glob("*.py") if f.name != "__init__.py"]

    assert len(files_to_check) > 0, "No domain files found"

    failed_files = []

    for file_path in files_to_check:
        with open(file_path) as f:
            first_line = f.readline().strip()

        if expected_header not in first_line:
            failed_files.append(file_path.name)

    if failed_files:
        pytest.fail(
            f"❌ These files have wrong version headers:\n  "
            + "\n  ".join(failed_files)
            + f"\n\nExpected: {expected_header}\n"
            f">>> Run: python generate_latest_domain.py"
        )


def test_schema_has_version_in_description(schema_files):
    """
    Test that each schema file has the correct VERSION in its description.

    Args:
        schema_files: Path to the schema files to test
    """

    for schema, schema_file in schema_files.items():

        # Load the schema
        with open(schema_file, "r", encoding="utf-8") as f:
            schema = json.load(f)

        # Check that description key exists
        assert "description" in schema, f"{schema_file} is missing 'description' key"

        description = schema["description"]

        assert VERSION in description, (
            f"{schema_file} description does not contain VERSION '{VERSION}'. "
            f"Description: {description}"
        )


def test_index_html_has_correct_version(index_html_path):
    """
    Test that the index.html file contains the correct VERSION in the version badge.

    Looks for pattern: <span class="version-badge">Version X.Y.Z</span>
    """
    # Read the HTML file
    with open(index_html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Check if the file contains any version badge
    version_badge_pattern = r'<span class="version-badge">Version ([^<]+)</span>'
    match = re.search(version_badge_pattern, html_content)

    assert match, (
        f"Could not find version badge in {index_html_path}. "
        f'Expected pattern: <span class="version-badge">Version X.Y.Z</span>'
    )

    # Extract the version from HTML
    html_version = match.group(1).strip()

    # Compare with the VERSION from cdf package
    assert html_version == VERSION, (
        f"Version mismatch in {index_html_path}:\n"
        f"  HTML version: {html_version}\n"
        f"  Expected (from cdf.VERSION): {VERSION}\n"
        f"Please update the version in index.html to match cdf.VERSION"
    )
