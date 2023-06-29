import os

from beartype import beartype
from click.testing import CliRunner
from click_skeleton.testing import run_cli

from musicbot.main import cli

from . import fixtures


@beartype
def test_youtube_search(cli_runner: CliRunner) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "youtube",
            "search",
            "buckethead",
            "welcome to bucketheadland",
        ],
    )


@beartype
def test_youtube_download(cli_runner: CliRunner) -> None:
    try:
        _ = run_cli(
            cli_runner,
            cli,
            [
                "--quiet",
                "youtube",
                "download",
                "buckethead",
                "welcome to bucketheadland",
                "--path",
                "test.mp3",
            ],
        )
    finally:
        try:
            os.remove("test.mp3")
        except OSError:
            pass


@beartype
def test_youtube_fingerprint(cli_runner: CliRunner) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "youtube",
            "fingerprint",
            fixtures.youtube_url,
        ],
    )


@beartype
def test_youtube_find(cli_runner: CliRunner) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "youtube",
            "find",
            str(fixtures.folder_mp3),
            str(fixtures.one_mp3),
        ],
    )
