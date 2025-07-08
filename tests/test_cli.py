"""
Testing cli logic
"""
import sys

import pytest

from asta_s_eu.scraping.kleinanzeigen_de import cli


def test_version() -> None:
    """
    GIVEN --version argument
    WHEN execute cli
    THEN show version and exit with error code 0
    """
    sys.argv = [sys.argv[0], "--version"]
    with pytest.raises(SystemExit) as a:
        cli.cli()

    assert a.value.code == 0
