import re
import json
import jsonschema
import pathlib
import jsonlines
from importlib import resources
from typing import Literal
from io import StringIO


from . import VERSION

from .custom import validate_formation

SKIP_SNAKE_CASE = [
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

CUSTOM_VALIDATORS = {"formation": validate_formation}


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

    def validate_schema(self, sample):
        """Validate the instance against the schema plus snake_case etc"""
        instance = self._load_sample(sample)

        self.errors = []

        # Validate against JSON schema
        self.validator.validate(instance)

        # Additional validation for snake_case etc.
        self._validate_item(instance, [])

        if self.errors:
            print("A validation error occurred...")
            for error in self.errors:
                print(error)
        else:
            print(
                f"Your {self.validator_type().capitalize()}Data schema is valid for version {VERSION}."
            )

    def _validate_item(self, item, path):
        """Recursively validate items in the data structure"""
        if isinstance(item, dict):
            # Validate dictionary keys
            for key, value in item.items():
                # Check if key is snake_case
                if key in SKIP_SNAKE_CASE:
                    continue
                elif key in CUSTOM_VALIDATORS:
                    if not CUSTOM_VALIDATORS[key](value):
                        self.errors.append(
                            f"Key '{'.'.join(path + [key])}' failed custom validation with value {value}"
                        )
                if not self.is_snake_case(key):
                    self.errors.append(
                        f"Key '{'.'.join(path + [key])}' is not in snake_case value {value}"
                    )

                # Recursively validate nested items
                self._validate_item(value, path + [key])

        elif isinstance(item, list):
            # Validate list items
            for i, value in enumerate(item):
                self._validate_item(value, path + [str(i)])

        elif isinstance(item, str):
            current_path = ".".join(path) if path else "root"
            # Only check snake_case for fields that look like identifiers
            if re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", item) and not re.match(
                r"^[0-9]+$", item
            ):
                if not self.is_snake_case(item):
                    self.errors.append(
                        f"String value at '{current_path}' is not in snake_case value {item}"
                    )
