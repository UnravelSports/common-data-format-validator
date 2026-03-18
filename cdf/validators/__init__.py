from importlib import resources

VERSION = "0.2.3"

from .validators import (
    MetaSchemaValidator,
    MatchSchemaValidator,
    EventSchemaValidator,
    TrackingSchemaValidator,
    SkeletalSchemaValidator,
    VideoSchemaValidator,
)

from .common import POSITION_GROUPS
