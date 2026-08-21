try:
    __CDFV_SETUP__
except NameError:
    __CDFV_SETUP__ = False

if not __CDFV_SETUP__:
    from .validators import (
        MetaSchemaValidator,
        MatchSchemaValidator,
        EventSchemaValidator,
        TrackingSchemaValidator,
        SkeletalSchemaValidator,
        LandmarkSchemaValidator,
        VideoSchemaValidator,
        VERSION,
    )

__version__ = "0.1.0-alpha"
