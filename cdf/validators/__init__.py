from pathlib import Path

__cdf_version__ = "0.2.0"
__version__ = "0.0.1"

SCHEMA_PATH = Path("cdf", "files", "schema")

from .common import SchemaValidator
from .validators import (
    MetaSchemaValidator,
    MatchSchemaValidator,
    EventSchemaValidator,
    TrackingSchemaValidator,
)
