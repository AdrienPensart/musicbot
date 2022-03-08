# type: ignore
import logging

import pytest
from click_skeleton.testing import run_cli

from musicbot.main import cli

from . import fixtures

logger = logging.getLogger(__name__)


@pytest.fixture(autouse=True)
def testmusics(cli_runner):
    run_cli(cli_runner, cli, [
        '--quiet',
        'local', 'scan',
        *fixtures.folders,
    ])
    yield
    run_cli(cli_runner, cli, [
        '--quiet',
        'local', 'clean',
        '--yes',
    ])
