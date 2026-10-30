"""Generate the paper's tables and JSON figures as copy-pasteable LaTeX.

Co-authors keep the paper's tables and JSON examples in step with the validator
by copying from here. Each table and each JSON figure produces:

    docs/latest/latex/<name>.txt    the LaTeX source, served as text so a
                                    browser shows it instead of downloading it
    docs/latest/latex/<name>.pdf    the same fragment rendered, to eyeball
                                    before pasting

Split tables stay split -- cdf-meta-optional and cdf-meta-optional-1 are two
files, because they are two tables in the paper and pasting them as one would
not fit the page.

The table wording here is the *paper's*, not the validator's. Those deliberately
differ for 73 fields, which is the whole reason this exists rather than being
derived from the schemas.

The JSON figures are the other way round: their content is cut down from the
version's sample files, keeping only the fields the schema requires, so a field
renamed in the schema shows up renamed in the paper. The hand-written listings
they replace had drifted from the schema and four of five were not valid JSON.
The captions are written for the paper by hand and kept in examples.json.

    python src/generate_latex.py                 text and PDFs
    python src/generate_latex.py --no-pdf        text only, no TeX needed
    python src/generate_latex.py --require-pdf   fail if TeX is missing
"""

import json
import os
import re

import jsonschema
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from cdf.validators import VERSION  # noqa: E402

FILES = ROOT / "cdf" / "files" / f"v{VERSION}"
TABLES = FILES / "latex" / "tables.json"
EXAMPLES = FILES / "latex" / "examples.json"
# The paper's own preamble, so a rendered table matches the paper exactly.
ASSETS = pathlib.Path(__file__).resolve().parent / "latex_assets"
OUT = ROOT / "docs" / "latest" / "latex"


# ---------------------------------------------------------------------
# Rendering a table back into LaTeX
#
# The rows hold the paper's own wording, which already contains LaTeX where
# the paper wants it -- $^\star$, \ref{...}, \textit{}. Those have to survive
# untouched while the surrounding prose gets escaped, so the escaper works
# span by span rather than character by character.
# ---------------------------------------------------------------------

# A math span or a command with its braced arguments. Anything matching this is
# already LaTeX and is copied through verbatim.
PROTECT = re.compile(r"\$[^$]*\$|~?\\[a-zA-Z]+(?:\{[^{}]*\})*")


# {i}, {home|away}, {event|tracking|video|...} -- the paper's notation for an
# index or a set of sibling roots.
ALTERNATION = re.compile(r"\{([a-z][a-z0-9_]*(?:\|[a-z][a-z0-9_]*)*)\}")


def _escape_plain(s):
    # Alternations first, while the text is still raw. Both halves matter: the
    # braces are consumed as grouping if left bare, and a bare "|" in OT1 text
    # mode renders as an em dash -- so {event|tracking|video} silently becomes
    # "event-tracking-video" rather than failing.
    s = ALTERNATION.sub(
        lambda m: r"\{" + r"\text{\textbar}".join(m.group(1).split("|")) + r"\}",
        s,
    )
    # TeX opens a quote with a backtick; a straight ' opens with a closing
    # glyph, so 'youth' renders as ’youth’. The content is required to hold no
    # whitespace so an apostrophe -- "the official's position" -- is never
    # mistaken for an opening quote.
    s = re.sub(r"'([^'\s]{1,40})'", r"`\1'", s)
    # A double quote is never an apostrophe, so it can safely span spaces --
    # which it needs to, for names like "Mohamed Salah Hamed Mahrous Ghaly".
    s = re.sub(r'"([^"]{1,80})"', r"``\1''", s)
    s = s.replace("&", r"\&").replace("%", r"\%").replace("#", r"\#")
    s = s.replace("_", r"\_")
    # OT1 renders a bare < or > as an inverted glyph, silently. A review
    # description once carried a literal "<dagger>" and compiled to garbage
    # without a warning, so these are escaped rather than trusted.
    s = s.replace("<", r"\textless{}").replace(">", r"\textgreater{}")
    return s


def esc(text):
    """Plain text -> LaTeX, leaving \\ref, math and other commands untouched."""
    if text is None:
        return ""
    out, i = [], 0
    for m in PROTECT.finditer(text):
        out.append(_escape_plain(text[i : m.start()]))
        out.append(m.group(0))
        i = m.end()
    out.append(_escape_plain(text[i:]))
    return re.sub(r"\s+", " ", "".join(out)).strip()


def render_table(table):
    """One table's complete LaTeX source, ready to paste into the paper."""
    lines = [table["tex"]["header"]]
    for row in table["rows"]:
        cells = [
            esc(row["root"]),
            esc(row["field"]),
            esc(row["description"]),
            esc(row["type"]),
        ]
        lines.append(" & ".join(cells) + r" \\")
    lines.append(table["tex"]["footer"])
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------
# Rendering a JSON figure from a sample file
#
# The sample files validate against their schema (tests/test_validators.py),
# so anything cut out of them carries the schema's current field names. The
# cut keeps the required fields, including those an if/then in the schema makes
# required -- has_extratime: true is what pulls first_half_extratime into the
# match figure.
# ---------------------------------------------------------------------

# Stand-ins for what a figure leaves out: list items, rendered "...", and whole
# objects named in an example's "omit", rendered "{...}" (an omitted list
# becomes [ELLIPSIS], so "[...]"). This is the paper's notation, and these are
# the only ways a listing departs from valid JSON.
ELLIPSIS = object()
OMITTED = object()

# Most listing lines a figure may have. A minipage cannot break across pages,
# so a taller figure runs off the bottom of the page in the paper -- and the
# preview PDFs cannot show that, because standalone.tex lengthens their page.
# Measured in the paper's preamble: the text height is 692.7pt, each listing
# line 9.5pt, and the rest of the figure 65.7pt with a two-line caption plus
# 11pt per further caption line. That fits 65 lines beside a two-line caption
# and 62 beside a five-line one; 60 keeps two lines spare at five.
MAX_LINES = 60

# Longest listing line, in characters. The listing sits in a 0.8\linewidth
# minipage, 409.7pt in the paper's preamble, and lstlisting sets each character
# in a fixed 0.6em column: 5.1pt, since the footnotesize typewriter em is 8.5pt.
# So 80 characters fit and the 81st wraps mid-string (compiled and checked).
# 76 keeps four columns spare.
WIDTH = 76
INDENT = "    "


def _resolve(schema, root):
    while "$ref" in schema:
        # Every $ref in the schemas is local: "#/definitions/<name>".
        schema = root["definitions"][schema["$ref"].split("/")[-1]]
    return schema


def _applicable(schemas, data, root):
    """The subschemas governing `data`, with each if/then/else branch that applies."""

    def branch(cond):
        # A condition sits either on the schema itself (match.periods: play_direction
        # unless shootout) or inside its allOf (event: official_id for referees).
        if "if" not in cond:
            return []
        holds = jsonschema.Draft7Validator(cond["if"]).is_valid(data)
        taken = cond.get("then" if holds else "else")
        return [taken] if taken else []

    out = []
    for schema in schemas:
        schema = _resolve(schema, root)
        out += [schema] + branch(schema)
        for cond in schema.get("allOf", []):
            out += branch(cond) if "if" in cond else [cond]
    return out


def prune(data, schemas, root, max_items, key=None):
    """`data` reduced to its required fields, with lists cut short.

    `schemas` is every subschema that applies at this point, because an if/then
    can add requirements to a child -- match.result gains its extratime keys
    from a condition on match.status.
    """
    if isinstance(data, dict):
        applicable = _applicable(schemas, data, root)
        required = set().union(*(s.get("required", []) for s in applicable))
        return {
            k: prune(
                v,
                [
                    s["properties"][k]
                    for s in applicable
                    if isinstance(s.get("properties", {}).get(k), dict)
                ],
                root,
                max_items,
                key=k,
            )
            for k, v in data.items()
            if k in required
        }
    if isinstance(data, list):
        items = [
            _resolve(s, root)["items"] for s in schemas if "items" in _resolve(s, root)
        ]
        keep = max_items.get(key, max_items.get("default", 1))
        kept = [prune(v, items, root, max_items) for v in data[:keep]]
        return kept + [ELLIPSIS] if len(data) > keep else kept
    return data


def _scalar(v):
    if v is ELLIPSIS:
        return "..."
    if v is OMITTED:
        return "{...}"
    return json.dumps(v)


def render_json(value, used=0, level=0):
    """`value` as indented JSON, short flat objects on one line, ELLIPSIS as "..."."""
    if not isinstance(value, (dict, list)):
        return _scalar(value)
    items = list(value.items()) if isinstance(value, dict) else list(value)
    if not items:
        return "{}" if isinstance(value, dict) else "[]"
    opening, closing = ("{", "}") if isinstance(value, dict) else ("[", "]")

    def entry(item, used, level):
        if isinstance(value, dict):
            k, v = item
            prefix = f"{json.dumps(k)}: "
            return prefix + render_json(v, used + len(prefix), level)
        return render_json(item, used, level)

    flat = all(
        not isinstance(v, (dict, list)) or not v
        for v in (value.values() if isinstance(value, dict) else value)
    )
    if flat:
        line = opening + ", ".join(entry(i, 0, 0) for i in items) + closing
        # One column is held back for the comma the parent may append.
        if used + len(line) + 1 <= WIDTH:
            return line
    pad = INDENT * (level + 1)
    body = ",\n".join(pad + entry(i, len(pad), level + 1) for i in items)
    return f"{opening}\n{body}\n{INDENT * level}{closing}"


FIGURE = r"""\begin{center}
\begin{minipage}{0.8\linewidth}
\begin{lstlisting}
%s
\end{lstlisting}
\captionof{figure}{%s}
\label{%s}
\end{minipage}
\end{center}
"""


def example_records(example):
    """The sample records a figure shows, cut to their required fields."""
    schema = json.loads((FILES / "schema" / example["schema"]).read_text())
    sample = FILES / "sample" / example["sample"]
    if sample.suffix == ".jsonl":
        records = [json.loads(l) for l in sample.read_text().splitlines() if l]
        wanted = example.get("records", 1)
        if len(records) < wanted:
            # Showing fewer records than the caption promises would read as a
            # mistake in the paper, so fail rather than quietly shrink.
            raise SystemExit(
                f"{example['name']}: wants {wanted} records, {sample} has {len(records)}"
            )
        records = records[:wanted]
    else:
        records = [json.loads(sample.read_text())]
    return [prune(r, [schema], schema, example.get("max_items", {})) for r in records]


def _omit(record, path):
    """Replace the value at dotted `path` with its stand-in, in place."""
    *parents, last = path.split(".")
    for key in parents:
        record = record[key]
    # A KeyError here is a typo in examples.json, or a field the schema dropped.
    record[last] = [ELLIPSIS] if isinstance(record[last], list) else OMITTED


def render_example(example):
    """One JSON figure's complete LaTeX source, ready to paste into the paper."""
    rendered = []
    for record in example_records(example):
        for path in example.get("omit", []):
            _omit(record, path)
        rendered.append(render_json(record))
    listing = "\n".join(rendered)
    check_fits(example["name"], listing)
    return FIGURE % (listing, example["caption"], example["label"])


def check_fits(name, listing):
    """Fail unless `listing` fits the paper's page: see MAX_LINES and WIDTH."""
    lines = listing.split("\n")
    if len(lines) > MAX_LINES:
        raise SystemExit(
            f"{name}: {len(lines)} listing lines, but only {MAX_LINES} fit on a"
            " page. Add to its omit or max_items in examples.json."
        )
    for number, line in enumerate(lines, 1):
        # Only a single value can get here -- render_json breaks every object
        # and list that is too wide -- so the fix is in the sample file.
        if len(line) > WIDTH:
            raise SystemExit(
                f"{name}: listing line {number} is {len(line)} characters, but"
                f" only {WIDTH} fit without wrapping: {line.strip()[:60]}"
            )


# pdflatex stamps the current time into every PDF, so two runs a second apart
# produce different bytes and CI could never tell a stale PDF from a fresh one.
# SOURCE_DATE_EPOCH pins that stamp; the value is arbitrary but must not move.
BUILD_EPOCH = "1700000000"


def render_pdf(name, source, refs, out_dir):
    """Render one table on its own, using the paper's preamble.

    Returns True on success. A missing package is a plain failure rather than a
    crash: the text files are the deliverable, the PDF is a convenience.
    """
    env = dict(os.environ, SOURCE_DATE_EPOCH=BUILD_EPOCH, FORCE_SOURCE_DATE="1")
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        for asset in ("preamble.tex", "standalone.tex"):
            shutil.copy(ASSETS / asset, tmp / asset)
        (tmp / "fragment.tex").write_text(source)
        if refs:
            (tmp / "fragment.refs").write_text(refs)
        proc = subprocess.run(
            [
                "pdflatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
                f"-jobname={name}",
                r"\def\fragment{fragment}\input{standalone}",
            ],
            cwd=tmp,
            capture_output=True,
            text=True,
            env=env,
        )
        pdf = tmp / f"{name}.pdf"
        if proc.returncode != 0 or not pdf.exists():
            return False, proc.stdout[-400:]
        shutil.copy(pdf, out_dir / f"{name}.pdf")
        # Overfull boxes mean the table runs past the margin in the paper too.
        log = (tmp / f"{name}.log").read_text(errors="replace")
        overfull = log.count("Overfull \\hbox") + log.count("Overfull \\vbox")
        return True, overfull


PAGE = """<!doctype html>
<meta charset="utf-8">
<title>{title} - LaTeX</title>
<style>
  body {{ font: 15px/1.6 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
         max-width: 60rem; margin: 3rem auto; padding: 0 1.5rem; color: #24292f; }}
  h1 {{ font-size: 1.5rem; margin-bottom: .25rem; }}
  .lede {{ color: #57606a; margin-top: 0; }}
  .table-block {{ border: 1px solid #d0d7de; border-radius: 6px; margin: 1.5rem 0; }}
  .table-head {{ display: flex; justify-content: space-between; align-items: baseline;
                 gap: 1rem; padding: .75rem 1rem; border-bottom: 1px solid #d0d7de;
                 background: #f6f8fa; border-radius: 6px 6px 0 0; }}
  .table-head h2 {{ font-size: .95rem; margin: 0; font-family: ui-monospace, monospace; }}
  .meta {{ color: #57606a; font-size: .85rem; white-space: nowrap; }}
  .meta a {{ color: #0969da; }}
  pre {{ margin: 0; padding: 1rem; overflow-x: auto; font-size: 12px;
         background: #fff; border-radius: 0 0 6px 6px; }}
  footer {{ margin-top: 3rem; color: #57606a; font-size: .85rem;
            border-top: 1px solid #d0d7de; padding-top: 1rem; }}
  a {{ color: #0969da; }}
  .preview {{ font: inherit; font-size: .8rem; color: #0969da; background: #fff;
              border: 1px solid #d0d7de; border-radius: 4px; padding: 0 .5rem;
              margin-left: .25rem; cursor: pointer; }}
  .preview:hover {{ background: #f6f8fa; }}
  .preview.failed {{ color: #cf222e; }}
  .render {{ padding: 1rem; background: #fff; border-radius: 0 0 6px 6px;
             color: #57606a; font-size: .85rem; overflow-x: auto; }}
  .render canvas {{ display: block; max-width: 100%; height: auto; }}
</style>
<h1>{title}: LaTeX</h1>
<p class="lede">Copy a block straight into the paper. The tables carry the paper's
own wording, which differs from the schema's in places.{figure_note} All blocks
are regenerated from format version {version} whenever the schemas change.</p>
{blocks}
<footer>
  <a href="../../index.html">All schemas</a> &middot;
  <a href="../{schema_page}">{title} JSON Schema</a>
</footer>
<script src="preview.js" defer></script>
"""

FIGURE_NOTE = """ The JSON figure
is cut down from the format's sample file to the fields the schema requires, so its
field names always match the validator."""

BLOCK = """<div class="table-block">
  <div class="table-head">
    <h2>{name}</h2>
    <span class="meta">{count} &middot;
      <a href="{name}.txt">.txt</a>{pdf}</span>
  </div>
  <pre>{source}</pre>
</div>
"""

# Renders the PDF into the page in place of the source; see the script itself.
PREVIEW_JS = "preview.js"

# Which paper tables belong to which schema page, in the order the paper uses.
SCHEMA_TITLES = {
    "meta.json": "Meta Data",
    "event.json": "Event Data",
    "tracking.json": "Tracking Data",
    "match.json": "Match Data",
    "landmark.json": "Landmark Data",
    "video.json": "Video Data",
}


def escape_html(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def write_pages(data, examples, have_pdf):
    """One page per schema, listing that schema's tables, then its JSON figure."""
    by_schema = {}
    for table in data["tables"]:
        count = f"{len(table['rows'])} rows"
        by_schema.setdefault(table["schema"], []).append((table["name"], count))
    for example in examples:
        by_schema.setdefault(example["schema"], []).append(
            (example["name"], "JSON figure")
        )

    shutil.copy(ASSETS / PREVIEW_JS, OUT / PREVIEW_JS)
    for schema, entries in by_schema.items():
        blocks = []
        for name, count in entries:
            # Link a PDF that exists on disk even if this run did not build one.
            # A --no-pdf run used to silently strip working links from the pages.
            pdf = (
                f' &middot; <a href="{name}.pdf">.pdf</a>'
                f' <button class="preview" data-pdf="{name}.pdf">Preview</button>'
                if name in have_pdf or (OUT / f"{name}.pdf").exists()
                else ""
            )
            blocks.append(
                BLOCK.format(
                    name=name,
                    count=count,
                    pdf=pdf,
                    source=escape_html((OUT / f"{name}.txt").read_text()),
                )
            )
        stem = schema.replace(".json", "")
        has_figure = any(e["schema"] == schema for e in examples)
        (OUT / f"{stem}.html").write_text(
            PAGE.format(
                title=SCHEMA_TITLES.get(schema, stem),
                version=data["version"],
                figure_note=FIGURE_NOTE if has_figure else "",
                blocks="\n".join(blocks),
                schema_page=schema.replace(".json", ".html"),
            )
        )
    return sorted(by_schema)


def main():
    want_pdf = "--no-pdf" not in sys.argv
    require_pdf = "--require-pdf" in sys.argv
    if want_pdf and not shutil.which("pdflatex"):
        if require_pdf:
            # Falling back to text-only here would leave the committed PDFs
            # stale while reporting success, which is the one outcome the
            # pre-commit guard exists to prevent.
            print("  pdflatex not found, and --require-pdf was given.")
            print("  The PDFs are committed because CI cannot rebuild them")
            print("  reproducibly, so they have to be regenerated here.")
            print("  Install TeX Live, or pass --no-pdf to skip deliberately.")
            return 1
        print("  pdflatex not found; writing text only")
        want_pdf = False

    for needed in (TABLES, EXAMPLES):
        if not needed.exists():
            # Usually a VERSION bump made before the new version's folder was
            # complete. Stopping here leaves docs/ as it was.
            print(
                f"  VERSION is {VERSION}, but {needed.relative_to(ROOT)} does not exist."
            )
            print("  Copy it from the previous version's folder.")
            return 1

    data = json.loads(TABLES.read_text())
    examples = json.loads(EXAMPLES.read_text())["examples"]
    OUT.mkdir(parents=True, exist_ok=True)

    fragments = [
        (
            t["name"],
            render_table(t),
            t["tex"].get("refs", ""),
            f"{len(t['rows']):3} rows",
        )
        for t in data["tables"]
    ] + [(e["name"], render_example(e), e["refs"], "JSON figure") for e in examples]

    failed = []
    made, have_pdf = 0, set()
    for name, source, refs, what in fragments:
        (OUT / f"{name}.txt").write_text(source)
        made += 1
        line = f"  {name:28} {what}"
        if want_pdf:
            ok, detail = render_pdf(name, source, refs, OUT)
            if not ok:
                failed.append(name)
                line += "   PDF FAILED"
                print(line)
                print(f"      {detail}")
                continue
            have_pdf.add(name)
            line += f"   pdf{'  ' + str(detail) + ' overfull' if detail else ''}"
        print(line)

    pages = write_pages(data, examples, have_pdf)
    print(f"\n  {made} fragments, {len(pages)} pages -> {OUT.relative_to(ROOT)}")
    print(f"  format version {data['version']}")

    # A failed render leaves the previous PDF in place, so a staleness check
    # would see no diff and pass. Fail loudly instead -- otherwise a missing
    # TeX package silently stops the PDFs being rebuilt at all.
    if failed:
        print(f"\n  {len(failed)} PDF(s) failed to render: {', '.join(failed)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
