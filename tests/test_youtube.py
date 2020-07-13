import os
import pytest
from musicbot.cli import cli
from . import fixtures
from .conftest import run_cli


@pytest.mark.runner_setup(mix_stderr=False)
def test_youtube_search(cli_runner):
    run_cli(cli_runner, cli, ['youtube', 'search', 'buckethead', 'welcome to bucketheadland'])


@pytest.mark.runner_setup(mix_stderr=False)
def test_youtube_download(cli_runner):
    try:
        run_cli(cli_runner, cli, ['youtube', 'download', 'buckethead', 'welcome to bucketheadland', '--path', 'test.mp3'])
    finally:
        try:
            os.remove('test.mp3')
        except OSError:
            pass


@pytest.mark.runner_setup(mix_stderr=False)
def test_youtube_fingerprint(cli_runner):
    run_cli(cli_runner, cli, ['youtube', 'fingerprint', fixtures.youtube_url])


@pytest.mark.runner_setup(mix_stderr=False)
def test_youtube_find(cli_runner):
    run_cli(cli_runner, cli, ['youtube', 'find', fixtures.one_mp3])