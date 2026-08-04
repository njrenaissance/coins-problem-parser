"""Shared pytest configuration and fixtures."""

from pathlib import Path

import pytest

from fakecoin import Strategy, parse

_SAMPLE_PATH = Path(__file__).resolve().parent.parent / "spec" / "sample_solution.txt"


def pytest_configure(config):
    """Show live log output at INFO under `pytest -v`, unless a log-cli level was set explicitly."""
    if config.option.verbose > 0 and config.option.log_cli_level is None:
        config.option.log_cli_level = "INFO"


@pytest.fixture(scope="session")
def sample_path() -> Path:
    """Filesystem path to the reference 12-coin / 3-weighing solution."""
    return _SAMPLE_PATH


@pytest.fixture(scope="session")
def sample_strategy() -> Strategy:
    """The reference solution, parsed once for the whole test session."""
    return parse(_SAMPLE_PATH.read_text(encoding="utf-8"))
