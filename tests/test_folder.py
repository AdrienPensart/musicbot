import pytest
from musicbot.cli import cli
from musicbot.click_helpers import run_cli
from . import fixtures


@pytest.mark.runner_setup(mix_stderr=False)
def test_folder_flac2mp3(cli_runner):
    run_cli(cli_runner, cli, ['folder', 'flac2mp3', '--dry', *fixtures.folders])


@pytest.mark.runner_setup(mix_stderr=False)
def test_folder_tracks(cli_runner):
    run_cli(cli_runner, cli, ['folder', 'tracks', *fixtures.folders])


@pytest.mark.runner_setup(mix_stderr=False)
def test_folder_check_consistency(cli_runner):
    run_cli(cli_runner, cli, ['folder', 'consistency', *fixtures.folders])
