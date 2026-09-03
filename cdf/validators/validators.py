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


class LandmarkSchemaValidator(SchemaValidator):
    @classmethod
    def validator_type(cls):
        return "landmark"


class SkeletalSchemaValidator(LandmarkSchemaValidator):
    """Deprecated alias for LandmarkSchemaValidator.

    Within the CDF, 'skeletal' has been renamed to 'landmark'. This validates
    against the same schema as LandmarkSchemaValidator and differs only in
    emitting a deprecation warning.
    """

    def __init__(self, *args, **kwargs):
        warnings.warn(
            "SkeletalSchemaValidator is deprecated: within the CDF, 'skeletal' has "
            "been replaced with 'landmark'. Use LandmarkSchemaValidator instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)


class VideoSchemaValidator(SchemaValidator):
    @classmethod
    def validator_type(cls):
        return "video"
