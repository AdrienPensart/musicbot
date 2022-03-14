# type: ignore
import json
import logging

import pytest
from click_skeleton.testing import run_cli

from musicbot.main import cli

from . import fixtures

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def testmusics(cli_runner):
    output = run_cli(cli_runner, cli, [
        '--quiet',
        'local', 'scan',
        '--clean',
        '--output', 'json',
        *fixtures.folders,
    ])
    json.loads(output)
    yield output
    run_cli(cli_runner, cli, [
        '--quiet',
        'local', 'clean',
        '--yes',
    ])
