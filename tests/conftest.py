import os

import pytest

# Modules whose tests require HF dataset access
_HF_MODULES = {
    "tests.backend.test_submission_api",
    "tests.tasks.evaluation",
}


def _needs_hf(item):
    """Return True if the test item belongs to a module that requires HF_TOKEN."""
    module = item.module.__name__
    return any(module.startswith(prefix) for prefix in _HF_MODULES)


def pytest_collection_modifyitems(config, items):  # pylint: disable=unused-argument
    """Skip tests that need HF dataset access when HF_TOKEN is unavailable."""
    if os.environ.get("HF_TOKEN"):
        return
    skip_marker = pytest.mark.skip(
        reason="HF_TOKEN not set — skipping tests that require Hugging Face access"
    )
    for item in items:
        if _needs_hf(item):
            item.add_marker(skip_marker)
