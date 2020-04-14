import pytest
from musicbot.cli import cli
from . import fixtures
from .conftest import run_cli


@pytest.mark.runner_setup(mix_stderr=False)
def test_folder_flac2mp3(cli_runner):
    run_cli(cli_runner, cli, ['folder', 'flac2mp3', '--dry', *fixtures.folders])


@pytest.mark.runner_setup(mix_stderr=False)
def test_folder_tracks(cli_runner):
    run_cli(cli_runner, cli, ['folder', 'tracks', *fixtures.folders])


@pytest.mark.runner_setup(mix_stderr=False)
def test_folder_check_consistency(cli_runner):
    run_cli(cli_runner, cli, ['folder', 'check-consistency', *fixtures.folders])
