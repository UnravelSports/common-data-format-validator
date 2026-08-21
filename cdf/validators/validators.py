import warnings

from .common import SchemaValidator


class MetaSchemaValidator(SchemaValidator):
    @classmethod
    def validator_type(cls):
        return "meta"


class MatchSchemaValidator(SchemaValidator):
    @classmethod
    def validator_type(cls):
        return "match"


class EventSchemaValidator(SchemaValidator):
    @classmethod
    def validator_type(cls):
        return "event"


class TrackingSchemaValidator(SchemaValidator):
    @classmethod
    def validator_type(cls):
        return "tracking"


class SkeletalSchemaValidator(SchemaValidator):
    def __init__(self, *args, **kwargs):
        # Only warn for the deprecated class itself, not its LandmarkSchemaValidator subclass.
        if type(self) is SkeletalSchemaValidator:
            warnings.warn(
                "SkeletalSchemaValidator is deprecated: within the CDF, 'skeletal' has "
                "been replaced with 'landmark'. Use LandmarkSchemaValidator instead.",
                DeprecationWarning,
                stacklevel=2,
            )
        super().__init__(*args, **kwargs)

    @classmethod
    def validator_type(cls):
        return "skeletal"


class LandmarkSchemaValidator(SkeletalSchemaValidator):
    """Pass-through replacement for the deprecated SkeletalSchemaValidator.

    Within the CDF, 'skeletal' has been renamed to 'landmark'. This validator
    behaves identically to SkeletalSchemaValidator (it validates against the same
    schema) but does not emit the deprecation warning.
    """


class VideoSchemaValidator(SchemaValidator):
    @classmethod
    def validator_type(cls):
        return "video"
