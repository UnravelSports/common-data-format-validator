import re
import json
import jsonschema
import pathlib
import jsonlines
from importlib import resources
from typing import Literal
from io import StringIO


from . import __cdf_version__, SCHEMA_PATH

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
            schema = SCHEMA_PATH / f"{self.validator_type()}_v{__cdf_version__}.json"

        # Handle schema as either dict or path to JSON file
        if not isinstance(schema, dict):
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
    def _load_json(path, folder: Literal["schema", "sample"] = "schema"):
        """Internal utility to load JSON files from disk or package resources."""
        # If file exists on disk, load it directly
        if isinstance(path, pathlib.Path) and path.exists():
            with open(path, "r") as f:
                return json.load(f)

        # Otherwise, try loading from package resources
        filename = (
            path.name if isinstance(path, pathlib.Path) else pathlib.Path(path).name
        )

        try:
            with resources.files(f"cdf.files.{folder}").joinpath(filename).open(
                "r"
            ) as f:
                return json.load(f)
        except (FileNotFoundError, ValueError, ModuleNotFoundError):
            raise FileNotFoundError(
                f"JSON file '{filename}' not found on disk or in package resources ({folder})."
            )

    def _load_sample(self, sample):
        # If sample is a dictionary, return it directly
        if isinstance(sample, dict):
            return sample

        # Convert to Path if it's a string
        sample_path = pathlib.Path(sample) if isinstance(sample, str) else sample

        # Handle JSONL files
        if sample_path.suffix.lower() == ".jsonl":
            # If file exists on disk, use jsonlines
            if sample_path.exists() and sample_path.is_file():
                with jsonlines.open(sample_path) as reader:
                    for i, json_object in enumerate(reader, 1):
                        return json_object  # Return the first object
            else:
                # For package resources, read the content and use jsonlines reader
                try:
                    filename = sample_path.name
                    content = (
                        resources.files("cdf.files.sample")
                        .joinpath(filename)
                        .read_text()
                    )
                    reader = jsonlines.Reader(StringIO(content))
                    for i, json_object in enumerate(reader, 1):
                        return json_object  # Return the first object
                except (FileNotFoundError, ValueError, ModuleNotFoundError):
                    raise FileNotFoundError(
                        f"Sample JSONL file not found: {sample_path}"
                    )

        # Handle JSON files
        elif sample_path.suffix.lower() == ".json" or not sample_path.exists():
            try:
                return self._load_json(sample_path, folder="sample")
            except FileNotFoundError:
                raise FileNotFoundError(f"Sample JSON file not found: {sample_path}")

        # Invalid file type
        else:
            raise ValueError(
                f"Sample must be a dictionary or a valid path to a JSON/JSONL file, got {sample_path.suffix}"
            )

    def _load_schema(self, schema):
        # If schema is a dictionary, return it directly
        if isinstance(schema, dict):
            return schema

        # Convert to Path if it's a string
        schema_path = pathlib.Path(schema) if isinstance(schema, str) else schema

        # Validate file extension if it exists on disk
        if schema_path.exists() and schema_path.is_file():
            if schema_path.suffix.lower() != ".json":
                raise ValueError(
                    f"Schema must be a dictionary or a valid path to a JSON file, got {schema_path.suffix}"
                )

        # Try to load the file
        try:
            return self._load_json(schema_path, folder="schema")
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Schema file not found: {schema_path}")

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
                f"Your {self.validator_type().capitalize()}Data schema is valid for version {__cdf_version__}."
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
                        f"String value at '{current_path}' is not in snake_case  value {value}"
                    )
