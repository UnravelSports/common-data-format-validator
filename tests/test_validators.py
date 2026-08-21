import pytest
import os
from pathlib import Path
import sys
import json
import re
import warnings

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
    LandmarkSchemaValidator,
    VideoSchemaValidator,
    VERSION,
)
from cdf.validators.custom import ValidationWarning
from jsonschema import Draft7Validator
from jsonschema.exceptions import ValidationError


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
def landmark_validator():
    return LandmarkSchemaValidator()


@pytest.fixture
def video_validator():
    return VideoSchemaValidator()


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
        "video": SAMPLE_PATH / f"v{VERSION}" / "sample" / f"video.json",
    }


@pytest.fixture
def schema_files():
    return {
        "tracking": SAMPLE_PATH / f"v{VERSION}" / "schema" / f"tracking.json",
        "meta": SAMPLE_PATH / f"v{VERSION}" / "schema" / f"meta.json",
        "event": SAMPLE_PATH / f"v{VERSION}" / "schema" / f"event.json",
        "match": SAMPLE_PATH / f"v{VERSION}" / "schema" / f"match.json",
        "skeletal": SAMPLE_PATH / f"v{VERSION}" / "schema" / f"skeletal.json",
        "video": SAMPLE_PATH / f"v{VERSION}" / "schema" / f"video.json",
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


def test_skeletal_schema_validation(skeletal_validator, sample_files):
    """Test that skeletal schema validation runs without errors."""
    result = skeletal_validator.validate_schema(sample=sample_files["skeletal"])
    assert result is None or result is True


def test_landmark_schema_validation(landmark_validator, sample_files):
    """LandmarkSchemaValidator is a pass-through of the skeletal validator."""
    result = landmark_validator.validate_schema(sample=sample_files["skeletal"])
    assert result is None or result is True


def test_landmark_validator_does_not_warn(sample_files):
    """The replacement validator must not emit the skeletal deprecation warning."""
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        LandmarkSchemaValidator().validate_schema(sample=sample_files["skeletal"])


def test_skeletal_validator_is_deprecated():
    """SkeletalSchemaValidator warns that 'skeletal' was replaced with 'landmark'."""
    with pytest.warns(DeprecationWarning, match="replaced with 'landmark'"):
        SkeletalSchemaValidator()


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

    with pytest.warns(ValidationWarning):
        tracking_validator.validate_schema(sample=str(invalid_file), mode="soft")

    # Expect validation to fail
    with pytest.raises(ValidationError):  # Replace with specific exception if known
        tracking_validator.validate_schema(sample=str(invalid_file), mode="strict")


def test_skeletal_schema_validation_failure(skeletal_validator, tmp_path):
    """Test that skeletal schema validation fails with invalid data."""
    invalid_file = tmp_path / "invalid_skeletal.jsonl"
    with open(invalid_file, "w") as f:
        f.write('{"invalid_key": "invalid_value"}\n')

    with pytest.warns(ValidationWarning):
        skeletal_validator.validate_schema(sample=str(invalid_file), mode="soft")

    with pytest.raises(ValidationError):
        skeletal_validator.validate_schema(sample=str(invalid_file), mode="strict")


def _write_tracking_frames(tmp_path, frame_ids):
    """Write a tracking JSONL file reusing the packaged sample line, one line per frame_id."""
    base_path = SAMPLE_PATH / f"v{VERSION}" / "sample" / "tracking.jsonl"
    with open(base_path) as f:
        base = json.loads(f.readline())
    out = tmp_path / "frames.jsonl"
    with open(out, "w") as f:
        for fid in frame_ids:
            base["frame_id"] = fid
            f.write(json.dumps(base) + "\n")
    return out


def test_frame_ids_valid_sequence(tracking_validator, tmp_path):
    """Full-file validation accepts frame_ids that increase uniquely from 0."""
    path = _write_tracking_frames(tmp_path, [0, 1, 2])
    # No warning / no raise means the frame_id sequence check passed.
    tracking_validator.validate_schema(sample=str(path), limit=None, mode="strict")


def test_frame_ids_must_start_at_zero(tracking_validator, tmp_path):
    """The first frame_id in a file must be 0."""
    path = _write_tracking_frames(tmp_path, [5, 6, 7])
    with pytest.raises(ValidationError, match="must start at 0"):
        tracking_validator.validate_schema(sample=str(path), limit=None, mode="strict")


def test_frame_ids_must_strictly_increase(tracking_validator, tmp_path):
    """A repeated (non-increasing) frame_id is rejected."""
    path = _write_tracking_frames(tmp_path, [0, 2, 2])
    with pytest.raises(ValidationError, match="monotonically increasing"):
        tracking_validator.validate_schema(sample=str(path), limit=None, mode="strict")


def test_frame_ids_not_checked_when_sampling(tracking_validator, tmp_path):
    """With a line limit (sampling), the whole-file frame_id check does not run."""
    path = _write_tracking_frames(tmp_path, [5, 6, 7])
    # limit=1 reads a single line, so the start-at-0 rule must not fire.
    tracking_validator.validate_schema(sample=str(path), limit=1, mode="strict")


def _write_tracking_with_extra_key(tmp_path):
    """Write a single valid tracking line with a typo'd extra key inside `ball`."""
    base_path = SAMPLE_PATH / f"v{VERSION}" / "sample" / "tracking.jsonl"
    with open(base_path) as f:
        obj = json.loads(f.readline())
    obj["ball"]["stattus"] = True  # typo of the real field `status`
    out = tmp_path / "extra_key.jsonl"
    with open(out, "w") as f:
        f.write(json.dumps(obj) + "\n")
    return out


@pytest.mark.parametrize("mode", ["soft", "strict"])
def test_unknown_key_warns_with_suggestion(tracking_validator, tmp_path, mode):
    """Unknown keys are surfaced as advisory warnings (with a suggestion) in soft/strict."""
    path = _write_tracking_with_extra_key(tmp_path)
    with pytest.warns(
        ValidationWarning, match=r"unknown field 'stattus'.*did you mean 'status'"
    ):
        tracking_validator.validate_schema(sample=str(path), mode=mode, limit=None)


def test_unknown_key_raises_in_extreme(tracking_validator, tmp_path):
    """In extreme mode an unknown key becomes a hard error."""
    path = _write_tracking_with_extra_key(tmp_path)
    with pytest.raises(ValidationError, match="unknown field 'stattus'"):
        tracking_validator.validate_schema(sample=str(path), mode="extreme", limit=None)


def test_soft_argument_is_deprecated(tracking_validator, sample_files):
    """The legacy `soft` boolean still works but emits a DeprecationWarning."""
    with pytest.warns(DeprecationWarning, match="'soft' argument is deprecated"):
        tracking_validator.validate_schema(sample=sample_files["tracking"], soft=True)


def test_invalid_mode_raises(tracking_validator, sample_files):
    """An unknown mode is rejected up front."""
    with pytest.raises(ValueError, match="mode must be one of"):
        tracking_validator.validate_schema(sample=sample_files["tracking"], mode="nope")


def _write_meta_with_periods(tmp_path, mutate):
    """Load the packaged meta sample, apply `mutate(periods)`, and write it out."""
    base_path = SAMPLE_PATH / f"v{VERSION}" / "sample" / "meta.json"
    with open(base_path) as f:
        meta = json.load(f)
    mutate(meta["match"]["periods"])
    out = tmp_path / "meta.json"
    with open(out, "w") as f:
        json.dump(meta, f)
    return out


def test_period_timestamps_out_of_order_rejected(meta_validator, tmp_path):
    """Period timestamps must be chronological across periods."""

    def mutate(periods):
        periods[1]["start_time"] = "2023-05-15T18:00:00Z"  # before the first half ends

    path = _write_meta_with_periods(tmp_path, mutate)
    with pytest.raises(ValidationError, match="chronological"):
        meta_validator.validate_schema(sample=str(path), mode="strict")


def test_period_end_time_before_start_time_rejected(meta_validator, tmp_path):
    """Within a period, end_time must not precede start_time."""

    def mutate(periods):
        periods[0]["end_time"] = "2023-05-15T19:00:00Z"  # before its own start_time

    path = _write_meta_with_periods(tmp_path, mutate)
    with pytest.raises(ValidationError, match="chronological"):
        meta_validator.validate_schema(sample=str(path), mode="strict")


@pytest.mark.parametrize(
    "bad_value",
    [
        "2023-05-15T19:45:00+01:00",  # not UTC
        "2023-05-15 19:45:00Z",  # space instead of 'T'
        "2023-13-45T19:45:00Z",  # impossible date
    ],
)
def test_period_timestamp_bad_format_rejected(meta_validator, tmp_path, bad_value):
    """Period timestamps must be well-formed RFC 3339 UTC."""

    def mutate(periods):
        periods[0]["start_time"] = bad_value

    path = _write_meta_with_periods(tmp_path, mutate)
    with pytest.raises(ValidationError, match="RFC 3339 UTC"):
        meta_validator.validate_schema(sample=str(path), mode="strict")


def test_period_timestamp_issue_warns_in_soft(meta_validator, tmp_path):
    """In soft mode a malformed period timestamp is a warning, not an error."""

    def mutate(periods):
        periods[0]["start_time"] = "not-a-timestamp"

    path = _write_meta_with_periods(tmp_path, mutate)
    with pytest.warns(ValidationWarning, match="RFC 3339 UTC"):
        meta_validator.validate_schema(sample=str(path), mode="soft")


def test_generic_utc_check_covers_non_meta_datetime(match_validator, tmp_path):
    """The UTC check is schema-driven: it flags a bad date-time even outside meta periods."""
    base_path = SAMPLE_PATH / f"v{VERSION}" / "sample" / "match.json"
    with open(base_path) as f:
        match = json.load(f)
    match["events"]["goals"][0][
        "time"
    ] = "2023-05-15T19:45:00+02:00"  # valid RFC 3339, not UTC
    out = tmp_path / "match.json"
    with open(out, "w") as f:
        json.dump(match, f)
    with pytest.raises(ValidationError, match="RFC 3339 UTC"):
        match_validator.validate_schema(sample=str(out), mode="strict")


def test_local_kickoff_time_exempt_from_utc(meta_validator, tmp_path):
    """local_kickoff_time is intentionally local and must not be flagged for non-UTC."""

    def mutate(periods):
        pass  # leave periods; the sample already has a +01:00 local_kickoff_time

    path = _write_meta_with_periods(tmp_path, mutate)
    # Sample's local_kickoff_time is '...+01:00'; extreme must still pass.
    meta_validator.validate_schema(sample=str(path), mode="extreme")


def test_frame_timestamps_must_be_chronological(tracking_validator, tmp_path):
    """Per-frame timestamps must not go backwards across the file."""
    base_path = SAMPLE_PATH / f"v{VERSION}" / "sample" / "tracking.jsonl"
    with open(base_path) as f:
        base = json.loads(f.readline())
    lines = []
    for fid, ts in [(0, "2023-10-01T12:00:00Z"), (1, "2023-10-01T11:59:00Z")]:
        obj = json.loads(json.dumps(base))
        obj["frame_id"], obj["timestamp"] = fid, ts
        lines.append(json.dumps(obj))
    out = tmp_path / "frames.jsonl"
    with open(out, "w") as f:
        f.write("\n".join(lines) + "\n")
    with pytest.raises(ValidationError, match="frame timestamps must be chronological"):
        tracking_validator.validate_schema(sample=str(out), mode="strict", limit=None)


def test_whistle_timestamps_must_be_chronological(meta_validator, tmp_path):
    """Meta whistle timestamps must be chronological."""
    base_path = SAMPLE_PATH / f"v{VERSION}" / "sample" / "meta.json"
    with open(base_path) as f:
        meta = json.load(f)
    meta["match"]["whistles"][2]["time"] = "2023-05-15T10:00:00Z"  # out of order
    out = tmp_path / "meta.json"
    with open(out, "w") as f:
        json.dump(meta, f)
    with pytest.raises(
        ValidationError, match="whistle timestamps must be chronological"
    ):
        meta_validator.validate_schema(sample=str(out), mode="strict")


def test_all_samples_pass_extreme(
    tracking_validator,
    meta_validator,
    event_validator,
    match_validator,
    landmark_validator,
    video_validator,
    sample_files,
):
    """Every packaged sample must have zero unknown/undefined keys (extreme mode).

    This guards against schema/sample field-name drift going unnoticed, which the
    open (additionalProperties-permissive) schemas would otherwise hide.
    """
    cases = {
        "tracking": tracking_validator,
        "meta": meta_validator,
        "event": event_validator,
        "match": match_validator,
        "skeletal": landmark_validator,
        "video": video_validator,
    }
    for name, validator in cases.items():
        validator.validate_schema(sample=sample_files[name], mode="extreme", limit=None)


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


# ---------------------------------------------------------------------------
# v0.3.0 schema consistency and behaviour
# ---------------------------------------------------------------------------


def _load_schema(schema_files, name):
    """Load one of the packaged schemas as a dict."""
    with open(schema_files[name], "r", encoding="utf-8") as f:
        return json.load(f)


def _event_errors(schema_files, record):
    """Validate a single event record against the event sub-schema."""
    schema = _load_schema(schema_files, "event")["properties"]["event"]
    return [
        error.message for error in Draft7Validator(schema).iter_errors(record["event"])
    ]


@pytest.fixture
def event_record(sample_files):
    """First record of the packaged event sample, as a mutable dict."""
    with open(sample_files["event"], "r", encoding="utf-8") as f:
        return json.loads(f.readline())


def test_officials_definition_identical_in_meta_and_match(schema_files):
    """
    meta.json and match.json both describe a match official. They silently drifted
    apart once already - different field sets, an enum in one and a free-form string
    in the other, nullable names in one and not the other - which made a valid meta
    official invalid as a match official. Keeping the two definitions equal is the
    only thing preventing that from recurring.
    """
    meta_official = _load_schema(schema_files, "meta")["properties"]["officials"][
        "items"
    ]
    match_official = _load_schema(schema_files, "match")["properties"]["officials"][
        "items"
    ]

    assert meta_official == match_official, (
        "officials[i] must be defined identically in meta.json and match.json.\n"
        f"  meta  keys: {sorted(meta_official.get('properties', {}))}\n"
        f"  match keys: {sorted(match_official.get('properties', {}))}"
    )


def test_renamed_keys_absent_from_every_schema():
    """
    Guard against a partially applied rename. tracking.json and skeletal.json carry
    `officials` but no sample data exercises it, so a rename missed in those two
    files would pass every other test in this suite unnoticed.
    """
    schema_dir = SAMPLE_PATH / f"v{VERSION}" / "schema"
    retired = (
        '"referees"',
        '"official_type"',
        '"stadium":',
        '"time_start"',
        '"time_end"',
    )

    for schema_path in sorted(schema_dir.glob("*.json")):
        contents = schema_path.read_text(encoding="utf-8")
        for old_key in retired:
            assert (
                old_key not in contents
            ), f"{schema_path} still contains the retired key {old_key}"


def test_end_coordinates_may_be_null_for_single_point_events(
    schema_files, event_record
):
    """
    Single-point events - saves, duels, tackles, clearances - have no end coordinate.
    Copying x/y into x_end/y_end to satisfy a non-nullable schema fabricates a
    zero-length vector, so null has to be a legal encoding for them.
    """
    event_record["event"].update(type="save", x_end=None, y_end=None)

    assert _event_errors(schema_files, event_record) == []


def test_end_coordinates_must_be_numeric_for_deliveries(schema_files, event_record):
    """
    Passes and shots always have an end coordinate, so widening the base type must
    not let null through for them. This is the half of the conditional that breaks
    silently if the `if` is written without its own `required`, because draft-07
    matches `properties` vacuously when the key is absent.
    """
    for delivery in ("pass", "shot"):
        event_record["event"].update(type=delivery, x_end=None, y_end=None)

        assert _event_errors(
            schema_files, event_record
        ), f"null x_end/y_end must be rejected for type={delivery!r}"


def test_body_part_accepts_widened_values(schema_files, event_record):
    """The widened enum has to cover goalkeeper and non-foot contacts."""
    event_record["event"].update(type="save", x_end=None, y_end=None)

    for body_part in ("hands", "upper_body", "lower_body"):
        event_record["event"]["body_part"] = body_part
        assert _event_errors(schema_files, event_record) == [], body_part


def test_body_part_rejects_overlapping_values(schema_files, event_record):
    """
    `feet`, `body` and `chest` were considered and deliberately left out: each one
    overlaps a value already in the enum, and two vendors would encode the same
    touch differently. Their absence is a decision, not an oversight.
    """
    event_record["event"].update(type="save", x_end=None, y_end=None)

    for body_part in ("feet", "body", "chest"):
        event_record["event"]["body_part"] = body_part
        assert _event_errors(schema_files, event_record), body_part


def test_receiver_identifiers_accept_vendor_style_ids(
    event_validator, tmp_path, event_record
):
    """
    Real feeds identify players and teams as 'P1011' / 'T1002', not snake_case.
    receiver_id and receiver_team_id are exempt from value-level snake_case for the
    same reason team_id and player_id already are - without the exemption a
    perfectly valid file is rejected outright in strict mode.
    """
    event_record["event"].update(receiver_id="P1011", receiver_team_id="T1002")
    sample = tmp_path / "event.jsonl"
    sample.write_text(json.dumps(event_record) + "\n", encoding="utf-8")

    event_validator.validate_schema(sample=sample, mode="strict", limit=None)


def test_extratime_blocks_required_only_when_extratime_was_played(schema_files):
    """
    The extratime and shootout result blocks are conditional on status.has_extratime
    and status.has_shootout. That condition used to sit on `result`, which cannot see
    its sibling `status`, so it matched vacuously and fired on every match - an
    ordinary 2-1 regulation win was rejected for missing extratime it never played.
    """
    match_object = _load_schema(schema_files, "match")["properties"]["match"]
    validator = Draft7Validator(match_object)

    result = {
        "final": {"home": 2, "away": 1},
        "final_winning_team_id": "team_789",
        "first_half": {"home": 1, "away": 0},
        "second_half": {"home": 1, "away": 1},
    }

    regulation = {
        "id": "match_1",
        "status": {"is_neutral": False, "has_extratime": False, "has_shootout": False},
        "result": result,
    }
    assert [e.message for e in validator.iter_errors(regulation)] == []

    went_to_extratime = {
        "id": "match_2",
        "status": {"is_neutral": False, "has_extratime": True, "has_shootout": True},
        "result": result,
    }
    missing = [e.message for e in validator.iter_errors(went_to_extratime)]
    assert any("first_half_extratime" in m for m in missing)
    assert any("shootout" in m for m in missing)


def test_cards_may_be_shown_during_a_shootout(schema_files):
    """
    Players are sent off during shootouts, so `cards` has to allow that period.
    Substitutions deliberately do not - you cannot make one once a shootout starts.
    """
    events = _load_schema(schema_files, "match")["properties"]["events"]["properties"]

    assert "shootout" in events["cards"]["items"]["properties"]["period"]["enum"]
    assert (
        "shootout"
        not in events["substitutions"]["items"]["properties"]["period"]["enum"]
    )
