import pytest
from click_skeleton import run_cli
from musicbot.cli import cli
from . import fixtures


@pytest.mark.runner_setup(mix_stderr=False)
def test_music_flac2mp3(cli_runner):
    run_cli(cli_runner, cli, ['music', 'flac2mp3', fixtures.one_flac, '--folder', '/tmp'])


@pytest.mark.runner_setup(mix_stderr=False)
def test_music_tags(cli_runner):
    run_cli(cli_runner, cli, ['music', 'tags', fixtures.one_flac])
    run_cli(cli_runner, cli, ['music', 'tags', fixtures.one_mp3])


@pytest.mark.runner_setup(mix_stderr=False)
def test_music_check_consistency(cli_runner):
    run_cli(cli_runner, cli, ['music', 'consistency', fixtures.one_flac])
    run_cli(cli_runner, cli, ['music', 'consistency', fixtures.one_mp3])
