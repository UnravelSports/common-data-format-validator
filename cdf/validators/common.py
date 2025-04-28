import re
import json
import jsonschema
import pathlib
import jsonlines


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
    def _load_json(path):
        with open(path, "r") as f:
            schema_dict = json.load(f)
        return schema_dict

    def _load_schema(self, schema):
        schema_path = pathlib.Path(schema)

        if schema_path.exists() and schema_path.is_file():
            if schema_path.suffix.lower() == ".json":
                return self._load_json(schema_path)

            else:
                raise ValueError(
                    f"Schema must be a dictionary or a valid path to a JSON file, got {type(schema)}"
                )
        else:
            raise FileNotFoundError(f"File not found: {schema_path}")

    def _load_sample(self, sample):
        sample_path = pathlib.Path(sample)

        if sample_path.exists() and sample_path.is_file():

            if sample_path.suffix.lower() == ".jsonl":
                with jsonlines.open(sample_path) as reader:
                    for i, json_object in enumerate(reader, 1):
                        return json_object
            elif sample_path.suffix.lower() == ".json":
                return self._load_json(sample_path)
            else:
                raise ValueError(
                    f"Tracking Sample must be a dictionary (of a single frame) or a valid path to a JSONLines file, got {type(sample_path)}"
                )
        else:
            raise FileNotFoundError(f"File not found: {sample_path}")

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
