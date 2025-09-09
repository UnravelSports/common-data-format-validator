from importlib import resources

VERSION = "0.2.1"

FILES_PATH = resources.files("cdf") / "files"

from .validators import (
    MetaSchemaValidator,
    MatchSchemaValidator,
    EventSchemaValidator,
    TrackingSchemaValidator,
    SkeletalSchemaValidator,
    VideoSchemaValidator,
)
