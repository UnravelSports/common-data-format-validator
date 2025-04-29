from pathlib import Path

__cdf_version__ = "0.2.0"

SCHEMA_PATH = Path("cdf", "files", "schema")

from .validators import (
    MetaSchemaValidator,
    MatchSchemaValidator,
    EventSchemaValidator,
    TrackingSchemaValidator,
    SkeletalSchemaValidator,
    VideoSchemaValidator,
)
