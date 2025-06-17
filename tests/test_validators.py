import pytest
import os
from pathlib import Path
import sys

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
