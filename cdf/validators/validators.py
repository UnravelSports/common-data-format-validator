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
