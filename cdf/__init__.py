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
        VideoSchemaValidator,
        VERSION,
    )

__version__ = "0.0.12"
