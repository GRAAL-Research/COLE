import os

import pytest


def pytest_collection_modifyitems(config, items):
    """Skip all tests when HF_TOKEN is not available (e.g. Dependabot PRs)."""
    if not os.environ.get("HF_TOKEN"):
        skip_marker = pytest.mark.skip(reason="HF_TOKEN not set — skipping tests that require Hugging Face access")
        for item in items:
            item.add_marker(skip_marker)
