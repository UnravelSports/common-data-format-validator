# ⚽ Common Data Format Schema Validator
JSON and JSONLines Schema Validition for the Soccer Common Data Format (Anzer et al. 2025)

----

### How To

#### 1. Install package

`pip install common-data-format-validator`

#### 2. Create your own schema
Create your data schema according to the Common Data Format specificiations for any of:
- Offical Match Data
- Meta Data
- Event Data
- Tracking Data
- Skeletal Tracking Data

#### 3. Test your schema
Once you have created your schema, you can check it's validity using the available SchemaValidators for each of the above mentioned data types.

```python
from cdf import (
    TrackingSchemaValidator, 
    MetaSchemaValidator, 
    EventSchemaValidator,
    MatchSchemaValidator    
)

# Example valid tracking data
validator = TrackingSchemaValidator()
validator.validate_schema(
    sample="cdf/files/sample/tracking_v0.2.0.jsonl"
)
```

----

### Note

The validator checks:
- All mandatory fields are provided
- Snake case is adhered for each key and for values (except for player names, city names, venue names etc.)
- Data types are correct (e.g. boolean, integer etc.)
- Value entries for specific fields are correct (e.g. period type can only be one of 5 values)
- Position groups and positions follow naming conventions in CDF Appendix C Figure 7

The validator (currently) does not check:
- British spelling
- Correct pitch dimensions
- Color codes are hex (e.g. #FFC107)
- If player_ids (or other ids) in meta are in tracking, event etc. or vice versa
- Position labels fit within the formation specifications

----

### Current Version of Common Data Format

This validator currently relies on CDF "alpha" version 2, but includes all logical changes not yet reflected in the text of this version, as discussed in the [Changelog](/CHANGELOG.md)

----

### Changelog

See [CHANGELOG.md](/CHANGELOG.md)