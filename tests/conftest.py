import sys

import pytest

# Keep in step with python_requires in setup.py.
MINIMUM_PYTHON = (3, 11)


def pytest_configure(config):
    """Stop early when the interpreter is older than the package supports.

    Without this the suite runs anyway and fails deep in the timestamp tests,
    because datetime.fromisoformat only parses a trailing 'Z' from 3.11 on. Twenty
    failures about RFC 3339 read as broken code rather than as the wrong Python,
    which is the part that costs time. It bites whenever pytest is picked up from
    PATH instead of from the project's environment, so it is checked here rather
    than in the pre-commit hook, where it would only cover one way of running.
    """
    if sys.version_info >= MINIMUM_PYTHON:
        return

    required = ".".join(str(part) for part in MINIMUM_PYTHON)
    running = ".".join(str(part) for part in sys.version_info[:3])
    pytest.exit(
        f"This package requires Python {required} or newer, but the tests are "
        f"running on {running} ({sys.executable}). Activate the project "
        f"environment, or invoke pytest with a {required}+ interpreter.",
        returncode=1,
    )
