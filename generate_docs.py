#!/usr/bin/env python3
"""
Generate JSON Schema documentation for all CDF schemas.
"""

import os
import re
import subprocess
import sys
from pathlib import Path

# Import VERSION from cdf package
from cdf import VERSION

# Define schema files to generate docs for
SCHEMAS = [
    "meta.json",
    "event.json",
    "match.json",
    "tracking.json",
    "landmark.json",
    "video.json",
]

# Landing page carries the version badge, kept in sync with VERSION
INDEX_PATH = Path("docs/index.html")
BADGE_PATTERN = re.compile(r'(<span class="version-badge">Version )[^<]*(</span>)')


def generate_schema_docs():
    """Generate HTML documentation for all schema files."""
    # Define paths
    schema_dir = Path(f"cdf/files/v{VERSION}/schema")
    output_dir = Path("docs/latest")

    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating documentation for CDF version {VERSION}")
    print(f"Schema directory: {schema_dir}")
    print(f"Output directory: {output_dir}")
    print("-" * 60)

    success_count = 0
    failed_count = 0

    for schema_file in SCHEMAS:
        input_path = schema_dir / schema_file
        output_path = output_dir / schema_file.replace(".json", ".html")

        if not input_path.exists():
            print(f"⚠ Warning: Schema file not found: {input_path}")
            failed_count += 1
            continue

        print(f"Generating: {schema_file} -> {output_path.name}")

        try:
            result = subprocess.run(
                [
                    "generate-schema-doc",
                    "--config",
                    "template_name=js",
                    str(input_path),
                    str(output_path),
                    "--config",
                    "collapse_long_descriptions=false",
                    # Omit the generation timestamp so output is byte-stable and
                    # the CI staleness check only fires on real schema changes
                    "--config",
                    "footer_show_time=false",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            print(f"✓ Generated: {output_path}")
            success_count += 1
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to generate {schema_file}")
            print(f"  Error: {e.stderr}")
            failed_count += 1
        except FileNotFoundError:
            print("✗ Error: generate-schema-doc command not found.")
            print("  Make sure json-schema-for-humans is installed:")
            print("  pip install json-schema-for-humans")
            return False

    print("-" * 60)
    print(f"Documentation generation complete!")
    print(f"Success: {success_count}/{len(SCHEMAS)}")
    if failed_count > 0:
        print(f"Failed: {failed_count}/{len(SCHEMAS)}")
    print(f"Output files are in: {output_dir}")

    return failed_count == 0


def update_index_badge():
    """Stamp the landing page version badge with VERSION."""
    if not INDEX_PATH.exists():
        print(f"✗ Error: {INDEX_PATH} not found")
        return False

    html = INDEX_PATH.read_text(encoding="utf-8")
    updated, count = BADGE_PATTERN.subn(rf"\g<1>{VERSION}\g<2>", html)

    if count == 0:
        print(f"✗ Error: no version badge found in {INDEX_PATH}")
        return False

    if updated != html:
        INDEX_PATH.write_text(updated, encoding="utf-8")
        print(f"✓ Updated version badge in {INDEX_PATH} -> Version {VERSION}")
    else:
        print(f"✓ Version badge in {INDEX_PATH} already at Version {VERSION}")

    return True


if __name__ == "__main__":
    schemas_ok = generate_schema_docs()
    badge_ok = update_index_badge()

    if not (schemas_ok and badge_ok):
        sys.exit(1)
