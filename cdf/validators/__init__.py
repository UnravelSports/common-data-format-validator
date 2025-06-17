from pathlib import Path

VERSION = "0.2.1"

FILES_PATH = Path("cdf", "files")

from .validators import (
    MetaSchemaValidator,
    MatchSchemaValidator,
    EventSchemaValidator,
    TrackingSchemaValidator,
    SkeletalSchemaValidator,
    VideoSchemaValidator,
)
