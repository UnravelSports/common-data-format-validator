# ⚽ Common Data Format Schema Validator
JSON and JSONLines Schema Validition for the Soccer Common Data Format.

> Anzer, G., Arnsmeyer, K., Bauer, P., Bekkers, J., Brefeld, U., Davis, J., Evans, N., Kempe, M., Robertson, S. J., Smith, J. W., & Van Haaren, J. (2025). Common Data Format (CDF)—a Standardized Format for Match-Data in Football (Soccer). [Unpublished manuscript / Preprint].

---

### Changelog

See [CHANGELOG.md](https://github.com/UnravelSports/common-data-format-validator/blob/main/CHANGELOG.md)

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
import cdf

# # Example valid tracking data
validator = cdf.TrackingSchemaValidator()
validator.validate_schema(sample=f"cdf/files/v{cdf.VERSION}/sample/tracking.jsonl")

# Example valid meta data
validator = cdf.MetaSchemaValidator()
validator.validate_schema(sample=f"cdf/files/v{cdf.VERSION}/sample/meta.json")

# Example valid event data
validator = cdf.EventSchemaValidator()
validator.validate_schema(sample=f"cdf/files/v{cdf.VERSION}/sample/event.jsonl")

# Example valid match data
validator = cdf.MatchSchemaValidator()
validator.validate_schema(sample=f"cdf/files/v{cdf.VERSION}/sample/match.json")

# Example valid skeletal data
validator = cdf.SkeletalSchemaValidator()
validator.validate_schema(sample=f"cdf/files/v{cdf.VERSION}/sample/skeletal.jsonl")

# Example valid video data
validator = cdf.VideoSchemaValidator()
validator.validate_schema(sample=f"cdf/files/v{cdf.VERSION}/sample/video.json")
```

----

### Note

The validator checks:
- All mandatory fields are provided
- Snake case is adhered for each key and for values (except for player names, city names, venue names etc.)
- Data types are correct (e.g. boolean, integer etc.)
- Value entries for specific fields are correct (e.g. period type can only be one of 5 values)
- [Position groups and positions follow naming conventions](https://github.com/UnravelSports/common-data-format-validator/blob/main/assets/positions-v0.2.0.pdf)

The validator (currently) does not check:
- Correct JSONLines line separator ('\n')
- Correct UTF-8 encoding
- [Correct pitch dimensions](https://github.com/UnravelSports/common-data-format-validator/blob/main/assets/pitch-dimensions-v0.2.0.pdf)
- British spelling
- Color codes are hex (e.g. #FFC107)
- If player_ids (or other ids) in meta are in tracking, event etc. or vice versa
- Position labels fit within the formation specifications


----

### Current Version of Common Data Format

This validator currently relies on CDF "alpha" version 2, but includes all logical changes not yet reflected in the text of this version, as discussed in the [Changelog](https://github.com/UnravelSports/common-data-format-validator/blob/main/CHANGELOG.md)

----

Software by [Joris Bekkers](https://www.linkedin.com/in/joris-bekkers-33138288/)