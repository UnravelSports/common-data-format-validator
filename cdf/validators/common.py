import re
import copy
import json
import difflib
import warnings
import datetime
import jsonschema
import pathlib
import jsonlines
from importlib import resources
from typing import Literal
from io import StringIO


from . import VERSION

from .custom import validate_formation, ValidationWarning

# Sentinel so we can tell whether the deprecated `soft` argument was actually passed.
_UNSET = object()

# RFC 3339 date-time restricted to UTC: trailing 'Z' or '+00:00', optional fractional seconds.
# (The CDF records period times in UTC; RFC 3339 is the profile of ISO 8601 that
# JSON Schema's "date-time" format uses.)
_UTC_TIMESTAMP_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|\+00:00)$"
)


def _parse_utc_timestamp(value):
    """Parse an RFC 3339 UTC timestamp, returning a datetime or None if invalid.

    Requires UTC ('Z' or '+00:00'); fromisoformat parses both directly from
    Python 3.11 on. The regex fixes the shape and the parse rejects impossible
    dates (e.g. month 13).
    """
    if not isinstance(value, str) or not _UTC_TIMESTAMP_RE.match(value):
        return None
    try:
        return datetime.datetime.fromisoformat(value)
    except ValueError:
        return None


# Validation strictness levels, from most to least permissive.
VALIDATION_MODES = ("soft", "strict", "extreme")

# date-time fields that are intentionally NOT in UTC and so are exempt from the UTC check.
LOCAL_DATETIME_FIELDS = {"local_kickoff_time"}


# Conditional branches list only the properties they constrain, never the whole
# object, so closing them would report every other key of that object as unknown.
CONDITIONAL_KEYWORDS = ("if", "then", "else")


def _inject_no_additional(node):
    """Recursively set ``additionalProperties: false`` on every object schema.

    Produces the "shadow" schema used to detect unknown/undefined keys. Only nodes
    that declare ``properties`` (i.e. object schemas) are closed; ``$ref`` nodes and
    non-object subschemas are left untouched, as are ``if``/``then``/``else``
    branches. The enclosing object is closed either way, which is what actually
    catches an unknown key.
    """
    if isinstance(node, dict):
        if "properties" in node and "additionalProperties" not in node:
            node["additionalProperties"] = False
        for key, value in node.items():
            if key in CONDITIONAL_KEYWORDS:
                continue
            _inject_no_additional(value)
    elif isinstance(node, list):
        for value in node:
            _inject_no_additional(value)
    return node


# Keys whose VALUES should skip snake_case validation
# (All keys themselves must always be snake_case)
SKIP_VALUE_SNAKE_CASE = [
    "country",
    "city",
    "name",
    "id",
    "team_id",
    "player_id",
    "first_name",
    "last_name",
    "full_name",
    "short_name",
    "maiden_name",
    "position_group",
    "position",
    "final_winning_team_id",
    "assist_id",
    "in_player_id",
    "out_player_id",
    "receiver_id",
    "receiver_team_id",
    "official_id",
]

# Position groups and their valid positions
POSITION_GROUPS = {
    "GK": ["GK"],
    "DF": ["LB", "LCB", "CB", "RCB", "RB"],
    "MF": ["LAM", "CAM", "RAM", "LM", "LCM", "CM", "RCM", "RM", "LDM", "CDM", "RDM"],
    "FW": ["LW", "LCF", "CF", "RCF", "RW"],
    "SUB": ["SUB"],
}

# Flatten to get all valid positions
VALID_POSITIONS = list(
    set([pos for positions in POSITION_GROUPS.values() for pos in positions])
)
VALID_POSITION_GROUPS = list(POSITION_GROUPS.keys())

# Coordinate bounds
X_MIN, X_MAX = -65.0, 65.0
Y_MIN, Y_MAX = -42.5, 42.5


def validate_hex_colour(value):
    """Validate hex colour format (e.g., #FFFFFF or #FFF)"""
    if not isinstance(value, str):
        return False
    # Check for valid hex colour pattern: # followed by 3 or 6 hex digits
    return bool(re.match(r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$", value))


def validate_coordinate(key, value):
    """Validate coordinate values"""
    if not isinstance(value, (int, float)):
        return False, f"Coordinate '{key}' must be a number"

    if key == "x":
        if not (X_MIN <= value <= X_MAX):
            return (
                False,
                f"x coordinate must be between {X_MIN} and {X_MAX}, got {value}",
            )
    elif key == "y":
        if not (Y_MIN <= value <= Y_MAX):
            return (
                False,
                f"y coordinate must be between {Y_MIN} and {Y_MAX}, got {value}",
            )

    return True, None


def validate_position_group(value):
    """Validate position_group values"""
    return value in VALID_POSITION_GROUPS


def validate_position(value):
    """Validate position values"""
    return value in VALID_POSITIONS


CUSTOM_VALIDATORS = {
    "formation": validate_formation,
    "position_group": validate_position_group,
    "position": validate_position,
}


class SchemaValidator:
    def __init__(self, schema=None, *args, **kwargs):
        if schema is None:
            # Use importlib.resources to access package data
            schema_files = resources.files("cdf") / "files" / f"v{VERSION}" / "schema"
            schema_path = schema_files / f"{self.validator_type()}.json"

            # Read the schema file
            with schema_path.open("r") as f:
                schema_dict = json.load(f)
        elif not isinstance(schema, dict):
            # Handle schema as path (for backwards compatibility)
            schema_dict = self._load_schema(schema)
        else:
            schema_dict = schema

        self.schema_dict = schema_dict
        self.validator = jsonschema.validators.Draft7Validator(
            schema_dict, *args, **kwargs
        )
        # Shadow schema with every object closed, used to flag unknown/undefined keys
        # as advisories (or, in "extreme" mode, as hard errors).
        self.shadow_validator = jsonschema.validators.Draft7Validator(
            _inject_no_additional(copy.deepcopy(schema_dict))
        )
        self.errors = []
        self.advisories = []
        self.current_file = None  # Track current file being validated

    @classmethod
    def validator_type(cls):
        """Override this method in subclasses to specify the validator type"""
        raise NotImplementedError(
            "Subclasses must implement the 'validator_type' property"
        )

    @staticmethod
    def _load_json_from_package(version, folder: Literal["schema", "sample"], filename):
        """Load JSON file from package resources."""
        file_path = resources.files("cdf") / "files" / f"v{version}" / folder / filename
        with file_path.open("r") as f:
            return json.load(f)

    def _load_sample(self, sample):
        # If sample is a dictionary, return it directly
        if isinstance(sample, dict):
            return sample

        # Convert to Path if it's a string
        sample_path = pathlib.Path(sample) if isinstance(sample, str) else sample

        # If file exists on disk, load it directly
        if sample_path.exists() and sample_path.is_file():
            if sample_path.suffix.lower() == ".jsonl":
                with jsonlines.open(sample_path) as reader:
                    for json_object in reader:
                        return json_object  # Return the first object
            elif sample_path.suffix.lower() == ".json":
                with open(sample_path, "r") as f:
                    return json.load(f)
            else:
                raise ValueError(
                    f"Sample must be a JSON or JSONL file, got {sample_path.suffix}"
                )

        # Otherwise, try loading from package resources
        filename = sample_path.name

        if filename.endswith(".jsonl"):
            try:
                content = (
                    resources.files("cdf")
                    / "files"
                    / f"v{VERSION}"
                    / "sample"
                    / filename
                ).read_text()
                reader = jsonlines.Reader(StringIO(content))
                for json_object in reader:
                    return json_object  # Return the first object
            except (FileNotFoundError, ValueError, ModuleNotFoundError):
                raise FileNotFoundError(f"Sample JSONL file not found: {filename}")
        elif filename.endswith(".json"):
            try:
                return self._load_json_from_package(VERSION, "sample", filename)
            except (FileNotFoundError, ValueError, ModuleNotFoundError):
                raise FileNotFoundError(f"Sample JSON file not found: {filename}")
        else:
            raise ValueError(
                f"Sample must be a dictionary or a valid path to a JSON/JSONL file"
            )

    def _load_schema(self, schema):
        # If schema is a dictionary, return it directly
        if isinstance(schema, dict):
            return schema

        # Convert to Path if it's a string
        schema_path = pathlib.Path(schema) if isinstance(schema, str) else schema

        # If file exists on disk, load it directly
        if schema_path.exists() and schema_path.is_file():
            if schema_path.suffix.lower() != ".json":
                raise ValueError(
                    f"Schema must be a JSON file, got {schema_path.suffix}"
                )
            with open(schema_path, "r") as f:
                return json.load(f)

        # Otherwise, try loading from package resources
        filename = schema_path.name

        if not filename.endswith(".json"):
            raise ValueError(f"Schema must be a JSON file, got {filename}")

        try:
            return self._load_json_from_package(VERSION, "schema", filename)
        except (FileNotFoundError, ValueError, ModuleNotFoundError):
            raise FileNotFoundError(f"Schema file not found: {filename}")

    def is_snake_case(self, s):
        """Check if string follows snake_case pattern (lowercase with underscores)"""
        return bool(re.match(r"^[a-z][a-z0-9_]*$", s))

    def _is_jsonl_file(self, sample):
        """Check if sample is a JSONL file path"""
        if isinstance(sample, (str, pathlib.Path)):
            sample_path = pathlib.Path(sample) if isinstance(sample, str) else sample
            if (
                sample_path.exists()
                and sample_path.is_file()
                and sample_path.suffix.lower() == ".jsonl"
            ):
                return True
        return False

    def _validate_jsonl_separator(self, file_path):
        """Validate that JSONL file uses \\n as separator"""
        with open(file_path, "rb") as f:
            content = f.read()

        # Check for incorrect line endings
        if b"\r\n" in content:
            self.errors.append(
                f"{file_path.name}: JSONL file uses '\\r\\n' (CRLF) as line separator. Must use '\\n' (LF) only."
            )
        elif b"\r" in content:
            self.errors.append(
                f"{file_path.name}: JSONL file uses '\\r' (CR) as line separator. Must use '\\n' (LF) only."
            )

    def validate_schema(
        self, sample, mode: str = "soft", limit: int = 1, *, soft=_UNSET
    ):
        """
        Validate the instance against the schema plus snake_case etc.

        Args:
            sample: Sample data to validate (dict, file path, or JSONL path)
            mode: Validation strictness, one of:
                  "soft"    - report every issue as a warning; never raises.
                  "strict"  - raise on schema violations; unknown/undefined keys warn.
                  "extreme" - as "strict", but unknown/undefined keys also raise.
            limit: Number of lines to validate for JSONL files only (default: 1, None: all lines)
                   This parameter is ignored for JSON files and dict samples
            soft: Deprecated. Use `mode` instead. soft=True maps to "soft",
                  soft=False maps to "strict".
        """
        mode = self._resolve_mode(mode, soft)

        # Check if sample is a JSONL file
        if self._is_jsonl_file(sample):
            sample_path = pathlib.Path(sample) if isinstance(sample, str) else sample
            self.current_file = sample_path.name
            self._validate_jsonl_file(sample_path, mode, limit)
            return

        # Check if sample is a JSON file
        if isinstance(sample, (str, pathlib.Path)):
            sample_path = pathlib.Path(sample) if isinstance(sample, str) else sample
            if sample_path.exists() and sample_path.is_file():
                self.current_file = sample_path.name

        # For non-JSONL samples (JSON files or dicts), validate single instance
        # The limit parameter is ignored for these types
        instance = self._load_sample(sample)
        self.errors = []
        self.advisories = []

        # Validate against JSON schema (collect rather than raise so `mode` governs it)
        for error in self.validator.iter_errors(instance):
            self.errors.append(
                f"{self._format_path(list(error.absolute_path))}: {error.message}"
            )

        # Additional validation for snake_case etc.
        self._validate_item(instance, [])

        # Advisory / hard check for unknown keys
        self._collect_unknown_keys(instance, [])

        # Every `format: date-time` value must be RFC 3339 UTC (except allowlisted locals).
        self._collect_datetime_format_issues(instance, [])

        # Meta period and whistle timestamps must be chronological.
        if self.validator_type() == "meta":
            self._validate_meta_chronology(instance)

        # A level final score has no winner unless a shootout settled it.
        if self.validator_type() == "match":
            self._validate_match_result(instance)

        self._report(mode)

    def _resolve_ref(self, schema):
        """Resolve a local ``$ref`` (e.g. '#/definitions/team') against the root schema."""
        if isinstance(schema, dict) and "$ref" in schema:
            node = self.schema_dict
            for part in schema["$ref"].lstrip("#/").split("/"):
                if not isinstance(node, dict) or part not in node:
                    return {}
                node = node[part]
            return node
        return schema

    def _iter_datetime_values(self, instance, schema, path):
        """Yield (path, value) for every instance value under a ``format: date-time`` node."""
        schema = self._resolve_ref(schema)
        if not isinstance(schema, dict):
            return
        if schema.get("format") == "date-time":
            if isinstance(instance, str):
                yield path, instance
            return
        if isinstance(instance, dict):
            properties = schema.get("properties", {})
            for key, value in instance.items():
                if key in properties:
                    yield from self._iter_datetime_values(
                        value, properties[key], [*path, key]
                    )
        elif isinstance(instance, list):
            items = schema.get("items")
            if isinstance(items, dict):
                for i, value in enumerate(instance):
                    yield from self._iter_datetime_values(value, items, [*path, str(i)])

    def _collect_datetime_format_issues(self, instance, path_prefix):
        """Flag every ``format: date-time`` value that is not a valid RFC 3339 UTC timestamp.

        Driven by the schema's own ``format`` declarations, so it covers all current and
        future date-time fields. Fields in LOCAL_DATETIME_FIELDS (intentionally local, e.g.
        `local_kickoff_time`) are exempt from the UTC requirement.
        """
        for path, value in self._iter_datetime_values(instance, self.schema_dict, []):
            if path and path[-1] in LOCAL_DATETIME_FIELDS:
                continue
            if _parse_utc_timestamp(value) is None:
                label = self._format_path([*path_prefix, *path])
                self.errors.append(
                    f"{label}: {value!r} is not a valid RFC 3339 UTC timestamp "
                    f"(e.g. '2023-05-15T19:45:00Z')."
                )

    def _check_chronological(self, sequence, kind):
        """Append an error for any timestamp earlier than the previous one in `sequence`.

        `sequence` is a list of (label, datetime) in document order.
        """
        for (prev_label, prev_dt), (label, dt) in zip(sequence, sequence[1:]):
            if dt < prev_dt:
                self.errors.append(
                    f"{label}: timestamp {dt.isoformat()} is earlier than "
                    f"{prev_label} ({prev_dt.isoformat()}); {kind} must be chronological."
                )

    def _validate_meta_chronology(self, instance):
        """Check that meta period and whistle timestamps are chronological.

        Timestamp formatting is handled by the generic UTC check; here we only order the
        already-parseable values. For periods, reading start_time then end_time across
        periods in document order covers both start-before-end within a period and
        non-overlapping order across periods.
        """
        if not isinstance(instance, dict):
            return
        match = instance.get("match")
        if not isinstance(match, dict):
            return

        periods = match.get("periods")
        if isinstance(periods, list):
            sequence = []
            for index, period in enumerate(periods):
                if not isinstance(period, dict):
                    continue
                for field in ("start_time", "end_time"):
                    parsed = _parse_utc_timestamp(period.get(field))
                    if parsed is not None:
                        label = self._format_path(
                            ["match", "periods", str(index), field]
                        )
                        sequence.append((label, parsed))
            self._check_chronological(sequence, "period timestamps")

        whistles = match.get("whistles")
        if isinstance(whistles, list):
            sequence = []
            for index, whistle in enumerate(whistles):
                if not isinstance(whistle, dict):
                    continue
                parsed = _parse_utc_timestamp(whistle.get("time"))
                if parsed is not None:
                    label = self._format_path(["match", "whistles", str(index), "time"])
                    sequence.append((label, parsed))
            self._check_chronological(sequence, "whistle timestamps")

    def _validate_match_result(self, instance):
        """Check that ``final_winning_team_id`` agrees with the final scoreline.

        A level final score has no winner unless the tie was settled on penalties,
        so the winner is null exactly when the scores are level and no ``shootout``
        block is present. JSON Schema cannot compare two sibling values to each
        other, which is why this lives here rather than in match.json.
        """
        if not isinstance(instance, dict):
            return
        match = instance.get("match")
        if not isinstance(match, dict):
            return
        result = match.get("result")
        if not isinstance(result, dict):
            return

        final = result.get("final")
        if not isinstance(final, dict):
            return
        home, away = final.get("home"), final.get("away")
        if not isinstance(home, int) or not isinstance(away, int):
            return

        shootout = result.get("shootout")
        settled_on_penalties = isinstance(shootout, dict)
        winner = result.get("final_winning_team_id")
        drawn = home == away and not settled_on_penalties
        label = self._format_path(["match", "result", "final_winning_team_id"])

        if drawn:
            if winner is not None:
                self.errors.append(
                    f"{label}: must be null when the final score is level "
                    f"({home}-{away}) and no shootout was played"
                )
            return

        if winner is None:
            self.errors.append(
                f"{label}: must name the winning team when the match was not drawn"
            )
            return

        # Work out who actually won, then check the named team is that team.
        if home != away:
            side, margin = (
                ("home", f"{home}-{away}")
                if home > away
                else (
                    "away",
                    f"{away}-{home}",
                )
            )
        else:
            shootout_home, shootout_away = shootout.get("home"), shootout.get("away")
            if not isinstance(shootout_home, int) or not isinstance(shootout_away, int):
                return
            if shootout_home == shootout_away:
                self.errors.append(
                    self._format_path(["match", "result", "shootout"])
                    + f": cannot end level ({shootout_home}-{shootout_away}); "
                    "a shootout decides the winner"
                )
                return
            side, margin = (
                ("home", f"{shootout_home}-{shootout_away}")
                if shootout_home > shootout_away
                else ("away", f"{shootout_away}-{shootout_home}")
            )

        teams = instance.get("teams")
        if not isinstance(teams, dict):
            return
        winning_team = teams.get(side)
        if not isinstance(winning_team, dict):
            return
        expected = winning_team.get("id")
        if not isinstance(expected, str) or winner == expected:
            return

        self.errors.append(
            f"{label}: is '{winner}', but the {side} team '{expected}' won {margin}"
            + (" on penalties" if home == away else "")
        )

    @staticmethod
    def _resolve_mode(mode, soft):
        """Resolve the effective validation mode, honouring the deprecated `soft` flag."""
        if soft is not _UNSET:
            warnings.warn(
                "The 'soft' argument is deprecated; use mode='soft'|'strict'|'extreme' "
                "instead. soft=True maps to mode='soft', soft=False maps to mode='strict'.",
                DeprecationWarning,
                stacklevel=3,
            )
            mode = "soft" if soft else "strict"
        if mode not in VALIDATION_MODES:
            raise ValueError(f"mode must be one of {VALIDATION_MODES}, got {mode!r}")
        return mode

    def _validate_jsonl_file(self, sample_path, mode: str, limit: int):
        """Validate JSONL file with optional line limit"""
        self.errors = []
        self.advisories = []

        # Validate line separator if validating more than 1 line
        if limit is None or limit > 1:
            self._validate_jsonl_separator(sample_path)

        # frame_id must be a monotonically increasing unique integer starting at 0.
        # This is a whole-file (cross-line) check, so it only runs when the full file is
        # validated (limit is None) and only for frame-based data (tracking/landmark).
        # frame_id and per-frame timestamp are whole-file (cross-line) checks, so they
        # only run for full-file validation (limit is None) of frame-based data.
        check_frame_sequence = limit is None and self.validator_type() in (
            "tracking",
            "landmark",
        )
        prev_frame_id = None
        prev_timestamp = None

        line_number = 0

        with jsonlines.open(sample_path) as reader:
            for json_object in reader:
                line_number += 1

                # Validate against JSON schema
                try:
                    self.validator.validate(json_object)
                except Exception as e:
                    self.errors.append(
                        f"{sample_path.name}/line_{line_number}: Schema validation failed - {str(e)}"
                    )

                # Additional validation
                self._validate_item(json_object, [f"line_{line_number}"])

                # Advisory / hard check for unknown keys
                self._collect_unknown_keys(json_object, [f"line_{line_number}"])

                # Every `format: date-time` value must be RFC 3339 UTC.
                self._collect_datetime_format_issues(
                    json_object, [f"line_{line_number}"]
                )

                if check_frame_sequence:
                    prev_frame_id = self._validate_frame_id(
                        json_object, line_number, prev_frame_id, sample_path.name
                    )
                    prev_timestamp = self._validate_frame_timestamp(
                        json_object, line_number, prev_timestamp, sample_path.name
                    )

                # Check if we've reached the limit
                if limit is not None and line_number >= limit:
                    break

        self._report(mode, lines_validated=line_number)

    def _validate_frame_timestamp(self, json_object, line_number, prev_dt, filename):
        """Check that per-frame `timestamp` is non-decreasing across the file.

        Timestamp formatting is handled by the generic UTC check, so unparseable values
        are skipped here. Returns the current timestamp to carry into the next line.
        """
        parsed = _parse_utc_timestamp(json_object.get("timestamp"))
        if parsed is None:
            return prev_dt
        if prev_dt is not None and parsed < prev_dt:
            self.errors.append(
                f"{filename}/line_{line_number}: timestamp {parsed.isoformat()} is earlier "
                f"than the previous frame ({prev_dt.isoformat()}); frame timestamps must be "
                f"chronological."
            )
        return parsed

    def _validate_frame_id(self, json_object, line_number, prev_frame_id, filename):
        """Check that frame_id forms a monotonically increasing unique integer sequence
        starting at 0 across the file.

        frame_id presence and integer type are already enforced by the JSON schema, so
        this only checks the cross-line sequence. Returns the current frame_id to carry
        into the next line (or the unchanged prev_frame_id when the value is unusable).
        """
        frame_id = json_object.get("frame_id")
        if not isinstance(frame_id, int) or isinstance(frame_id, bool):
            # Missing / non-integer frame_id is already reported by schema validation.
            return prev_frame_id

        if prev_frame_id is None and frame_id != 0:
            self.errors.append(
                f"{filename}/line_{line_number}: frame_id must start at 0, got {frame_id}."
            )
        elif prev_frame_id is not None and frame_id <= prev_frame_id:
            self.errors.append(
                f"{filename}/line_{line_number}: frame_id must be a monotonically increasing "
                f"unique integer ({frame_id} does not exceed previous {prev_frame_id})."
            )

        return frame_id

    def _collect_unknown_keys(self, instance, path_prefix):
        """Flag keys that are not defined anywhere in the schema.

        Uses the shadow schema (every object closed with additionalProperties: false)
        and keeps only the 'additionalProperties' findings, so genuine schema
        violations are left to the real validator. Each unknown key is reported with
        its path and, where possible, a 'did you mean?' suggestion. Findings go to
        self.advisories, which "soft"/"strict" warn on and "extreme" treats as errors.
        """
        for error in self.shadow_validator.iter_errors(instance):
            if error.validator != "additionalProperties":
                continue
            if not isinstance(error.instance, dict):
                continue

            defined = list(error.schema.get("properties", {}).keys())
            unknown = [key for key in error.instance if key not in defined]

            location = self._format_path(
                [*path_prefix, *(str(p) for p in error.absolute_path)]
            )
            for key in unknown:
                match = difflib.get_close_matches(key, defined, n=1)
                suggestion = f" - did you mean '{match[0]}'?" if match else ""
                self.advisories.append(f"{location}: unknown field '{key}'{suggestion}")

    def _report(self, mode: str, lines_validated: int = None):
        """Report collected errors and advisories according to the validation mode."""
        errors = self.errors
        advisories = self.advisories
        if mode == "extreme":
            # Unknown keys are promoted to hard errors.
            errors = errors + advisories
            advisories = []

        if errors:
            if mode in ("strict", "extreme"):
                from jsonschema.exceptions import ValidationError

                raise ValidationError(errors[0])
            for error in errors:  # soft
                warnings.warn(f"{error}", ValidationWarning)

        for advisory in advisories:
            warnings.warn(f"{advisory}", ValidationWarning)

        if errors or advisories:
            return

        if lines_validated is not None:
            print(
                f"Your {self.validator_type().capitalize()}Data schema is valid for version {VERSION}. "
                f"Validated {lines_validated} line(s)."
            )
        else:
            print(
                f"Your {self.validator_type().capitalize()}Data schema is valid for version {VERSION}."
            )

    def _format_path(self, path):
        """Format path with filename prefix if available"""
        path_str = ".".join(str(p) for p in path) if path else "root"
        if self.current_file:
            return f"{self.current_file}/{path_str}"
        return path_str

    def _validate_item(self, item, path):
        """Recursively validate items in the data structure"""
        if isinstance(item, dict):
            # Validate dictionary keys
            for key, value in item.items():
                # Check for American spelling of "color"
                if "color" in key.lower() and "colour" not in key.lower():
                    self.errors.append(
                        f"Key '{self._format_path(path + [key])}' uses American spelling 'color'. Please use British English spelling 'colour'"
                    )

                # Validate colour hex values
                if "colour" in key.lower():
                    if not validate_hex_colour(value):
                        self.errors.append(
                            f"Key '{self._format_path(path + [key])}' must be a valid hex colour (e.g., #FFFFFF or #FFF), got {value}"
                        )

                # Validate coordinates
                if key in ["x", "y"] and "camera" not in path:
                    is_valid, error_msg = validate_coordinate(key, value)
                    if not is_valid:
                        self.errors.append(
                            f"{error_msg} at path '{self._format_path(path + [key])}'"
                        )

                # Run custom validators (position, position_group, formation, etc.)
                if key in CUSTOM_VALIDATORS:
                    if not CUSTOM_VALIDATORS[key](value):
                        if key == "position_group":
                            self.errors.append(
                                f"Key '{self._format_path(path + [key])}' got {value}, must be one of {VALID_POSITION_GROUPS}"
                            )
                        elif key == "position":
                            self.errors.append(
                                f"Key '{self._format_path(path + [key])}' got {value}, must be one of {VALID_POSITIONS}"
                            )
                        else:
                            self.errors.append(
                                f"Key '{self._format_path(path + [key])}' failed custom validation with value {value}"
                            )

                # ALWAYS check if key itself is snake_case (no exceptions)
                if not self.is_snake_case(key):
                    self.errors.append(
                        f"Key '{self._format_path(path + [key])}' is not in snake_case"
                    )

                # Recursively validate nested items
                self._validate_item(value, path + [key])

        elif isinstance(item, list):
            # Validate list items
            for i, value in enumerate(item):
                self._validate_item(value, path + [str(i)])

        elif isinstance(item, str):
            # Check if parent key is one that should skip snake_case validation for values
            parent_key = path[-1] if path else None
            if parent_key in SKIP_VALUE_SNAKE_CASE:
                # Skip snake_case validation for values of these keys
                return

            current_path = self._format_path(path)
            # Only check snake_case for fields that look like identifiers
            if re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", item) and not re.match(
                r"^[0-9]+$", item
            ):
                if not self.is_snake_case(item):
                    self.errors.append(
                        f"String value at '{current_path}' is not in snake_case value {item}"
                    )
