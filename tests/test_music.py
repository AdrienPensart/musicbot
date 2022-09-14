# type: ignore
import pytest
from click_skeleton.testing import run_cli

from musicbot.main import cli

from . import fixtures


@pytest.mark.runner_setup(mix_stderr=False)
def test_music_flac2mp3(cli_runner):
    run_cli(cli_runner, cli, [
        '--quiet',
        'music', 'flac2mp3',
        str(fixtures.folder_flac),
        str(fixtures.one_flac),
        '/tmp',
    ])


@pytest.mark.runner_setup(mix_stderr=False)
def test_music_tags(cli_runner):
    run_cli(cli_runner, cli, [
        '--quiet',
        'music', 'tags',
        str(fixtures.folder_flac),
        str(fixtures.one_flac),
    ])
    run_cli(cli_runner, cli, [
        '--quiet',
        'music', 'tags',
        str(fixtures.folder_mp3),
        str(fixtures.one_mp3),
    ])


@pytest.mark.runner_setup(mix_stderr=False)
def test_music_set_tags(cli_runner):
    run_cli(cli_runner, cli, [
        '--quiet',
        'music', 'set-tags',
        str(fixtures.one_flac),
        '--rating', 0,
        '--dry',
    ])
    run_cli(cli_runner, cli, [
        '--quiet',
        'music', 'set-tags',
        str(fixtures.one_mp3),
        '--rating', 0,
        '--dry',
    ])


@pytest.mark.runner_setup(mix_stderr=False)
def test_music_issues(cli_runner):
    run_cli(cli_runner, cli, [
        '--quiet',
        'music', 'issues',
        str(fixtures.folder_flac),
        str(fixtures.one_flac),
    ])
    run_cli(cli_runner, cli, [
        '--quiet',
        'music', 'issues',
        str(fixtures.folder_mp3),
        str(fixtures.one_mp3),
    ])


@pytest.mark.runner_setup(mix_stderr=False)
def test_music_add_keywords(cli_runner):
    run_cli(cli_runner, cli, [
        '--quiet',
        'music', 'add-keywords',
        str(fixtures.folder_flac),
        str(fixtures.one_flac),
        'test', '--dry',
    ])
    run_cli(cli_runner, cli, [
        '--quiet',
        'music', 'add-keywords',
        str(fixtures.folder_mp3),
        str(fixtures.one_mp3),
        'test', '--dry',
    ])


@pytest.mark.runner_setup(mix_stderr=False)
def test_music_delete_keywords(cli_runner):
    run_cli(cli_runner, cli, [
        '--quiet',
        'music', 'delete-keywords',
        str(fixtures.folder_flac),
        str(fixtures.one_flac),
        'test', '--dry',
    ])
    run_cli(cli_runner, cli, [
        '--quiet',
        'music', 'delete-keywords',
        str(fixtures.folder_mp3),
        str(fixtures.one_mp3),
        'test', '--dry',
    ])
