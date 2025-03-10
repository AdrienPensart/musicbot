from beartype import beartype
from click.testing import CliRunner
from click_skeleton.testing import run_cli

from musicbot.main import cli
from musicbot.object import MusicbotObject

from . import fixtures


@beartype
def test_local_folders(cli_runner: CliRunner, dsn: str) -> None:
    output = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "local",
            "folders",
            "--dsn",
            dsn,
            "--output",
            "json",
        ],
    )
    assert MusicbotObject.loads_json(output) is not None


@beartype
def test_local_remove(cli_runner: CliRunner, dsn: str) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "local",
            "remove",
            str(fixtures.one_flac),
            str(fixtures.one_mp3),
            "--dsn",
            dsn,
        ],
    )


@beartype
def test_local_clean(cli_runner: CliRunner, dsn: str) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "local",
            "clean",
            "--dsn",
            dsn,
        ],
    )


@beartype
def test_local_watch(cli_runner: CliRunner, dsn: str) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "local",
            "watch",
            "--dsn",
            dsn,
            "--timeout",
            5,
            str(fixtures.folder_flac),
        ],
    )


@beartype
def test_local_artists(cli_runner: CliRunner, dsn: str) -> None:
    output = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "local",
            "artists",
            "--dsn",
            dsn,
            "--output",
            "json",
        ],
    )
    assert MusicbotObject.loads_json(output) is not None


@beartype
def test_local_sync(cli_runner: CliRunner, dsn: str) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "local",
            "sync",
            "--dsn",
            dsn,
            "--delete",
            "--yes",
            "/tmp",
            "--dry",
        ],
    )


@beartype
def test_local_playlist(cli_runner: CliRunner, dsn: str) -> None:
    output = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "local",
            "playlist",
            "--dsn",
            dsn,
            "--output",
            "json",
        ],
    )
    assert MusicbotObject.loads_json(output) is not None


@beartype
def test_local_bests(cli_runner: CliRunner, dsn: str) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "local",
            "bests",
            "--dsn",
            dsn,
            "/tmp",
            "--dry",
        ],
    )


@beartype
def test_local_scan(cli_runner: CliRunner, dsn: str) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "local",
            "scan",
            "--dsn",
            dsn,
            *fixtures.scan_folders,
        ],
    )


@beartype
def test_custom_playlists(cli_runner: CliRunner, dsn: str) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "local",
            "custom-playlists",
            "--dsn",
            dsn,
            "/tmp",
        ],
    )
