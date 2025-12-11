import re
import json
import jsonschema
import pathlib
import jsonlines
from importlib import resources
from typing import Literal
from io import StringIO


from . import VERSION

from .custom import validate_formation, ValidationWarning

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
    "short_name",
    "maiden_name",
    "position_group",
    "position",
    "final_winning_team_id",
    "assist_id",
    "in_player_id",
    "out_player_id",
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

        self.validator = jsonschema.validators.Draft7Validator(
            schema_dict, *args, **kwargs
        )
        self.errors = []
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

    def validate_schema(self, sample, soft: bool = True, limit: int = 1):
        """
        Validate the instance against the schema plus snake_case etc

        Args:
            sample: Sample data to validate (dict, file path, or JSONL path)
            soft: If True, emit warnings; if False, raise exceptions
            limit: Number of lines to validate for JSONL files only (default: 1, None: all lines)
                   This parameter is ignored for JSON files and dict samples
        """
        # Check if sample is a JSONL file
        if self._is_jsonl_file(sample):
            sample_path = pathlib.Path(sample) if isinstance(sample, str) else sample
            self.current_file = sample_path.name
            self._validate_jsonl_file(sample_path, soft, limit)
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

        # Validate against JSON schema
        self.validator.validate(instance)

        # Additional validation for snake_case etc.
        self._validate_item(instance, [])

        self._report_errors(soft)

    def _validate_jsonl_file(self, sample_path, soft: bool, limit: int):
        """Validate JSONL file with optional line limit"""
        self.errors = []

        # Validate line separator if validating more than 1 line
        if limit is None or limit > 1:
            self._validate_jsonl_separator(sample_path)

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

                # Check if we've reached the limit
                if limit is not None and line_number >= limit:
                    break

        self._report_errors(soft, lines_validated=line_number)

    def _report_errors(self, soft: bool, lines_validated: int = None):
        """Report validation errors"""
        if self.errors:
            for error in self.errors:
                if not soft:
                    from jsonschema.exceptions import ValidationError

                    raise ValidationError(error)
                else:
                    import warnings

                    warnings.warn(f"{error}", ValidationWarning)
        else:
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
        path_str = ".".join(path) if path else "root"
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
