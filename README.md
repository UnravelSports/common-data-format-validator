# ⚽ Common Data Format Schema Validator

JSON and JSONLines Schema Validition for the Soccer Common Data Format.

> Anzer, G., Arnsmeyer, K., Bauer, P., Bekkers, J., Brefeld, U., Davis, J., Evans, N., Kempe, M., Robertson, S. J., Smith, J. W., & Van Haaren, J. (2025). Common Data Format (CDF)—a Standardized Format for Match-Data in Football (Soccer). [Unpublished manuscript / Preprint].

---

### Changelog

See [CHANGELOG.md](https://github.com/UnravelSports/common-data-format-validator/blob/main/CHANGELOG.md)

---

### How To

#### 1. Install package

`pip install common-data-format-validator`

#### 2. Create your own schema

Create your data schema according to the Common Data Format specificiations for any of:

- Offical Match Data
- Meta Data
- Event Data
- Tracking Data
- Landmark Tracking Data
- Video Data

#### 3. Test your schema

Once you have created your schema, you can check it's validity using the available SchemaValidators for each of the above mentioned data types.

```python
import cdf

# # Example valid tracking data
validator = cdf.TrackingSchemaValidator()
validator.validate_schema(sample=f"cdf/files/v{cdf.VERSION}/sample/tracking.jsonl", limit=1)

# Example valid meta data
validator = cdf.MetaSchemaValidator()
validator.validate_schema(sample=f"cdf/files/v{cdf.VERSION}/sample/meta.json")

# Example valid event data
validator = cdf.EventSchemaValidator()
validator.validate_schema(sample=f"cdf/files/v{cdf.VERSION}/sample/event.jsonl", limit=1)

# Example valid match data
validator = cdf.MatchSchemaValidator()
validator.validate_schema(sample=f"cdf/files/v{cdf.VERSION}/sample/match.json")

# Example valid landmark data
validator = cdf.LandmarkSchemaValidator()
validator.validate_schema(sample=f"cdf/files/v{cdf.VERSION}/sample/landmark.jsonl", limit=1)

# Example valid video data
validator = cdf.VideoSchemaValidator()
validator.validate_schema(sample=f"cdf/files/v{cdf.VERSION}/sample/video.json")
```

##### Validation modes

`validate_schema` takes a `mode` that decides how findings are reported.

```python
validator = cdf.MetaSchemaValidator()

# Report everything, raise nothing. Useful for a first look at a new file.
validator.validate_schema(sample="my_meta.json", mode="soft")

# Fail on anything the schema forbids, but tolerate extra keys.
validator.validate_schema(sample="my_meta.json", mode="strict")

# Also fail on keys the CDF does not define, e.g. a typo or an extension.
validator.validate_schema(sample="my_meta.json", mode="extreme")
```

---



### Note

The validator checks:

- All mandatory fields are provided
- Snake case is adhered for each key and for values (except for player names, city names, venue names etc.)
- Data types are correct (e.g. boolean, integer etc.)
- Value entries for specific fields are correct (e.g. period type can only be one of 5 values)
- [Position groups and positions follow naming conventions](https://github.com/UnravelSports/common-data-format-validator/blob/main/assets/positions-v0.2.0.pdf)
- Color codes are hex (e.g. #FFC107)
- Position labels fit within the formation specifications
- [Correct pitch dimensions](https://github.com/UnravelSports/common-data-format-validator/blob/main/assets/pitch-dimensions-v0.2.0.pdf) (Simply checks if they are "x" between -65.0 and 65.0 and "y" between -42.5 and +42.5)
- Correct JSONLines line separator ('\n')
- Check multiple lines by setting `limit`. Only works for JSONL files. `limit=None` checks the whole file.

The validator (currently) does not check:

- Correct UTF-8 encoding
- British spelling (currently only for "color" / "colour" keys)
- If player_ids (or other ids) in meta are in tracking, event etc. or vice versa

##### Missing values

Where a field has no value the CDF distinguishes two cases. A `null` value means the field applies to that record but there is nothing to record, so an event that ends with nobody in possession carries `receiver_id: null`. An absent key means the field does not apply to that kind of record at all, so a `referee` event leaves out `player_id` and `team_id` and carries `official_id` instead.

---

### Contributing

Keep each commit to one change to the format. The schema edit, its sample and the regenerated output belong in the same commit, but two unrelated changes should be two commits, even where they touch the same schema. Essentially, a change is a request to edit / update / append the CDF. Each change needs to be reviewable on it's own.

The JSON Schemas in `cdf/files/v{VERSION}/schema/` are the source of truth. The domain models and the documentation site are both generated from them:

| Generated                                                     | Command                              |
| ------------------------------------------------------------- | ------------------------------------ |
| `cdf/domain/latest/*.py` (`TypedDict` models)             | `python generate_latest_domain.py` |
| `docs/` (the [cdf.football](https://www.cdf.football) pages) | `python generate_docs.py`          |

You do not need to update the domain models yourself. Changes to the format belong in the schema, and anything edited directly in `cdf/domain/latest/` or `docs/` is replaced the next time the generators run. CI regenerates both on every pull request and fails if the result differs from what was committed, so the two stay in step.

A change to the format is:

1. Edit the schema in `cdf/files/v{VERSION}/schema/`
2. Update the matching sample in `cdf/files/v{VERSION}/sample/` so it still validates
3. Run `python generate_latest_domain.py` and `python generate_docs.py`
4. Add a `CHANGELOG.md` entry under the table the change belongs to
5. Commit the schema, the sample and the regenerated output together

Both generators format their own output.

---

### Current Version of Common Data Format

This validator currently relies on CDF "alpha" version 2, but includes all logical changes not yet reflected in the text of this version, as discussed in the [Changelog](https://github.com/UnravelSports/common-data-format-validator/blob/main/CHANGELOG.md)

#### Two version numbers

The format and the package are versioned separately, so the two numbers do not match and are not meant to.

| | Read from | Currently |
| --- | --- | --- |
| CDF format | `cdf.VERSION` | 0.3.1 |
| Python package | `cdf.__version__` | 0.1.0 |

`cdf.VERSION` selects which schemas you validate against, in `cdf/files/v{VERSION}/`, and is the version the Changelog is written against. `cdf.__version__` is the release published to PyPI.

They move independently. A package release can fix a bug in the validator without the format changing, and a format change does not have to wait for one. For reference, package 0.0.14 shipped CDF 0.2.3.

---

Software by [Joris Bekkers](https://www.linkedin.com/in/joris-bekkers-33138288/)
