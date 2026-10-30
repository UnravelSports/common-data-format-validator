"""The paper's JSON figures must be valid CDF.

The hand-written figures they replace had drifted from the schema (stadium for
venue, outcome for is_successful) and four of the five were not valid JSON, and
nothing noticed. These tests are what notices now.
"""

import copy
import json
import re
import sys
from pathlib import Path

import jsonschema
import pytest

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

import generate_latex  # noqa: E402
from cdf import (  # noqa: E402
    EventSchemaValidator,
    LandmarkSchemaValidator,
    MatchSchemaValidator,
    MetaSchemaValidator,
    TrackingSchemaValidator,
)

VALIDATORS = {
    "event.json": EventSchemaValidator,
    "landmark.json": LandmarkSchemaValidator,
    "match.json": MatchSchemaValidator,
    "meta.json": MetaSchemaValidator,
    "tracking.json": TrackingSchemaValidator,
}

EXAMPLES = json.loads(generate_latex.EXAMPLES.read_text())["examples"]


def listing(example):
    source = generate_latex.render_example(example)
    found = re.search(r"\\begin\{lstlisting\}\n(.*)\n\\end\{lstlisting\}", source, re.S)
    return found.group(1)


def without_elisions(text):
    """The listing with the paper's "..." notation removed, which must leave JSON."""
    text = text.replace("{...}", "{}").replace("[...]", "[]")
    return re.sub(r",\s*\.\.\.(?=\s*[\]}])", "", text)


@pytest.mark.parametrize("example", EXAMPLES, ids=lambda e: e["name"])
def test_figure_is_json_apart_from_elisions(example):
    text = without_elisions(listing(example))
    decoder, i, records = json.JSONDecoder(), 0, 0
    while i < len(text):
        _, i = decoder.raw_decode(text, i)
        records += 1
        while i < len(text) and text[i].isspace():
            i += 1
    assert records == example.get("records", 1)


@pytest.mark.parametrize("example", EXAMPLES, ids=lambda e: e["name"])
def test_figure_content_validates_against_its_schema(example):
    # Strict mode raises on a missing or misnamed required field, so this also
    # fails if pruning drops a field that an if/then makes required.
    validator = VALIDATORS[example["schema"]]()
    for record in generate_latex.example_records(example):
        clean = json.loads(without_elisions(generate_latex.render_json(record)))
        validator.validate_schema(sample=clean, mode="strict")


def _key_paths(value, path=()):
    """Every dict key in `value`, as a path of keys and list indices."""
    if isinstance(value, dict):
        for k, v in value.items():
            yield path + (k,)
            yield from _key_paths(v, path + (k,))
    elif isinstance(value, list):
        for i, v in enumerate(value):
            yield from _key_paths(v, path + (i,))


@pytest.mark.parametrize("example", EXAMPLES, ids=lambda e: e["name"])
def test_figures_show_only_required_fields(example):
    # The captions promise the mandatory fields, and the samples also carry
    # optional ones (metrics, start_time, ...) that must not leak in. A field is
    # required exactly when deleting it breaks validation, so every field shown
    # must fail that test -- whatever schema construct made it required.
    schema = json.loads(
        (generate_latex.FILES / "schema" / example["schema"]).read_text()
    )
    validator = jsonschema.Draft7Validator(schema)
    for record in generate_latex.example_records(example):
        clean = json.loads(without_elisions(generate_latex.render_json(record)))
        assert validator.is_valid(clean)
        for path in _key_paths(clean):
            trimmed = copy.deepcopy(clean)
            parent = trimmed
            for step in path[:-1]:
                parent = parent[step]
            del parent[path[-1]]
            assert not validator.is_valid(trimmed), f"optional field shown: {path}"


def _lists(value, key=None):
    """Every list in `value`, with the key it sits under."""
    if isinstance(value, dict):
        for k, v in value.items():
            yield from _lists(v, k)
    elif isinstance(value, list):
        yield key, value
        for v in value:
            yield from _lists(v)


@pytest.mark.parametrize("example", EXAMPLES, ids=lambda e: e["name"])
def test_lists_are_cut_to_max_items(example):
    # A figure has to fit on one page, so every list shows at most max_items.
    limits = example.get("max_items", {})
    for record in generate_latex.example_records(example):
        for key, items in _lists(record):
            shown = [i for i in items if i is not generate_latex.ELLIPSIS]
            assert len(shown) <= limits.get(key, limits.get("default", 1)), key


@pytest.mark.parametrize("length", range(40, 58))
def test_inline_objects_leave_room_for_their_comma(length):
    # An inline object followed by a comma once rendered at 81 characters, one
    # past what fits, and wrapped in the paper. Every length is tried so the
    # object is sometimes exactly WIDTH wide before its comma.
    value = {"outer": {"inner": {"k": "x" * length}, "next": 1}}
    for line in generate_latex.render_json(value).split("\n"):
        assert len(line) <= generate_latex.WIDTH, line


def test_check_fits_enforces_the_page_limits():
    # The limits protect the paper, where an overlong figure runs off the page
    # and an overlong line wraps mid-string; the previews cannot show either.
    width, height = generate_latex.WIDTH, generate_latex.MAX_LINES
    generate_latex.check_fits("fits", "\n".join(["x" * width] * height))
    with pytest.raises(SystemExit):
        generate_latex.check_fits("too tall", "\n".join(["x"] * (height + 1)))
    with pytest.raises(SystemExit):
        generate_latex.check_fits("too wide", "x" * (width + 1))


def test_conditionally_required_fields_are_kept():
    # first_half_extratime is optional in the schema, but required once
    # has_extratime is true -- which the match sample sets.
    match = next(e for e in EXAMPLES if e["schema"] == "match.json")
    result = generate_latex.example_records(match)[0]["match"]["result"]
    assert {
        "first_half_extratime",
        "second_half_extratime",
        "shootout",
    } <= result.keys()


def test_page_limits_stay_within_what_was_measured():
    # Measured in the paper's preamble (see the comments on WIDTH and
    # MAX_LINES): 80 characters fit a line, and 62 lines fit beside a
    # five-line caption. Raising either limit past that lets figures wrap or
    # run off the page in the paper while every other test still passes.
    assert generate_latex.WIDTH <= 80
    assert generate_latex.MAX_LINES <= 62
