"""Generate the paper's tables as copy-pasteable LaTeX, one file per table.

Co-authors keep the paper's tables in step with the validator by copying from
here. Each of the 12 tables produces:

    docs/latest/latex/<table>.txt   the LaTeX source, served as text so a
                                    browser shows it instead of downloading it
    docs/latest/latex/<table>.pdf   the same table rendered, to eyeball before
                                    pasting

Split tables stay split -- cdf-meta-optional and cdf-meta-optional-1 are two
files, because they are two tables in the paper and pasting them as one would
not fit the page.

The wording here is the *paper's*, not the validator's. Those deliberately
differ for 73 fields, which is the whole reason this exists rather than being
derived from the schemas.

    python src/generate_latex.py                 text and PDFs
    python src/generate_latex.py --no-pdf        text only, no TeX needed
    python src/generate_latex.py --require-pdf   fail if TeX is missing
"""

import json
import os
import re
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from cdf.validators import VERSION  # noqa: E402

TABLES = ROOT / "cdf" / "files" / f"v{VERSION}" / "latex" / "tables.json"
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
<title>{title} - LaTeX tables</title>
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
</style>
<h1>{title}: LaTeX tables</h1>
<p class="lede">Copy a block straight into the paper. These carry the paper's own
wording, which differs from the schema's in places, and are regenerated from
format version {version} whenever the schemas change.</p>
{blocks}
<footer>
  <a href="../../index.html">All schemas</a> &middot;
  <a href="../{schema_page}">{title} JSON Schema</a>
</footer>
"""

BLOCK = """<div class="table-block">
  <div class="table-head">
    <h2>{name}</h2>
    <span class="meta">{rows} rows &middot;
      <a href="{name}.txt">.txt</a>{pdf}</span>
  </div>
  <pre>{source}</pre>
</div>
"""

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


def write_pages(data, have_pdf):
    """One page per schema, listing that schema's tables."""
    by_schema = {}
    for table in data["tables"]:
        by_schema.setdefault(table["schema"], []).append(table)

    for schema, tables in by_schema.items():
        blocks = []
        for t in tables:
            name = t["name"]
            # Link a PDF that exists on disk even if this run did not build one.
            # A --no-pdf run used to silently strip working links from the pages.
            pdf = (
                f' &middot; <a href="{name}.pdf">.pdf</a>'
                if name in have_pdf or (OUT / f"{name}.pdf").exists()
                else ""
            )
            blocks.append(
                BLOCK.format(
                    name=name,
                    rows=len(t["rows"]),
                    pdf=pdf,
                    source=escape_html((OUT / f"{name}.txt").read_text()),
                )
            )
        stem = schema.replace(".json", "")
        (OUT / f"{stem}.html").write_text(
            PAGE.format(
                title=SCHEMA_TITLES.get(schema, stem),
                version=data["version"],
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

    data = json.loads(TABLES.read_text())
    OUT.mkdir(parents=True, exist_ok=True)

    failed = []
    made, have_pdf = 0, set()
    for table in data["tables"]:
        name = table["name"]
        source = render_table(table)
        (OUT / f"{name}.txt").write_text(source)
        made += 1
        line = f"  {name:28} {len(table['rows']):3} rows"
        if want_pdf:
            ok, detail = render_pdf(name, source, table["tex"].get("refs", ""), OUT)
            if not ok:
                failed.append(name)
                line += "   PDF FAILED"
                print(line)
                print(f"      {detail}")
                continue
            have_pdf.add(name)
            line += f"   pdf{'  ' + str(detail) + ' overfull' if detail else ''}"
        print(line)

    pages = write_pages(data, have_pdf)
    print(f"\n  {made} tables, {len(pages)} pages -> {OUT.relative_to(ROOT)}")
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
