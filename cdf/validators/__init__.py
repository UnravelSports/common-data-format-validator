from importlib import resources

VERSION = "0.3.2"

from .validators import (
    MetaSchemaValidator,
    MatchSchemaValidator,
    EventSchemaValidator,
    TrackingSchemaValidator,
    SkeletalSchemaValidator,
    LandmarkSchemaValidator,
    VideoSchemaValidator,
)

from .common import POSITION_GROUPS
