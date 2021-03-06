import pytest
from click_skeleton.testing import run_cli
from musicbot.main import cli
from . import fixtures


@pytest.mark.runner_setup(mix_stderr=False)
def test_music_flac2mp3(cli_runner):
    run_cli(cli_runner, cli, [
        '--quiet',
        'music', 'flac2mp3',
        fixtures.one_flac,
        '--folder', '/tmp',
    ])


@pytest.mark.runner_setup(mix_stderr=False)
def test_music_tags(cli_runner):
    run_cli(cli_runner, cli, [
        '--quiet',
        'music', 'tags',
        fixtures.one_flac,
    ])
    run_cli(cli_runner, cli, [
        '--quiet',
        'music', 'tags',
        fixtures.one_mp3,
    ])


@pytest.mark.runner_setup(mix_stderr=False)
def test_music_check_consistency(cli_runner):
    run_cli(cli_runner, cli, [
        '--quiet',
        'music', 'consistency',
        fixtures.one_flac,
    ])
    run_cli(cli_runner, cli, [
        '--quiet',
        'music', 'consistency',
        fixtures.one_mp3,
    ])


@pytest.mark.runner_setup(mix_stderr=False)
def test_music_add_keywords(cli_runner):
    run_cli(cli_runner, cli, [
        '--quiet',
        'music', 'add-keywords',
        fixtures.one_flac,
        'test', '--dry',
    ])
    run_cli(cli_runner, cli, [
        '--quiet',
        'music', 'add-keywords',
        fixtures.one_mp3,
        'test', '--dry',
    ])


@pytest.mark.runner_setup(mix_stderr=False)
def test_music_delete_keywords(cli_runner):
    run_cli(cli_runner, cli, [
        '--quiet',
        'music', 'delete-keywords',
        fixtures.one_flac,
        'test', '--dry',
    ])
    run_cli(cli_runner, cli, [
        '--quiet',
        'music', 'delete-keywords',
        fixtures.one_mp3,
        'test', '--dry',
    ])
