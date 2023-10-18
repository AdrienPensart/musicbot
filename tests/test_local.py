from beartype import beartype
from click.testing import CliRunner
from click_skeleton.testing import run_cli

from musicbot.main import cli
from musicbot.object import MusicbotObject

from . import fixtures


@beartype
def test_local_folders(cli_runner: CliRunner, edgedb: str) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "local",
            "folders",
            "--dsn",
            edgedb,
        ],
    )


@beartype
def test_local_search(cli_runner: CliRunner, edgedb: str) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "local",
            "search",
            "1995",
            "--dsn",
            edgedb,
        ],
    )


@beartype
def test_local_remove(cli_runner: CliRunner, edgedb: str) -> None:
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
            edgedb,
        ],
    )


@beartype
def test_local_clean(cli_runner: CliRunner, edgedb: str) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "local",
            "clean",
            "--dsn",
            edgedb,
        ],
    )


@beartype
def test_local_watch(cli_runner: CliRunner, edgedb: str) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "local",
            "watch",
            "--dsn",
            edgedb,
            "--timeout",
            5,
            str(fixtures.folder_flac),
        ],
    )


@beartype
def test_local_artists(cli_runner: CliRunner, edgedb: str) -> None:
    output = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "local",
            "artists",
            "--dsn",
            edgedb,
            "--output",
            "json",
        ],
    )
    assert MusicbotObject.loads_json(output) is not None


@beartype
def test_local_sync(cli_runner: CliRunner, edgedb: str) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "local",
            "sync",
            "--dsn",
            edgedb,
            "--delete",
            "--yes",
            "/tmp",
            "--dry",
        ],
    )


@beartype
def test_local_playlist(cli_runner: CliRunner, edgedb: str) -> None:
    output = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "local",
            "playlist",
            "--dsn",
            edgedb,
            "--output",
            "json",
        ],
    )
    assert MusicbotObject.loads_json(output) is not None


@beartype
def test_local_bests(cli_runner: CliRunner, edgedb: str) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "local",
            "bests",
            "--dsn",
            edgedb,
            "/tmp",
            "--dry",
        ],
    )


@beartype
def test_local_player(cli_runner: CliRunner, edgedb: str) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "local",
            "player",
            "--vlc-params",
            "--vout=dummy --aout=dummy",
            "--dsn",
            edgedb,
        ],
    )


@beartype
def test_local_scan(cli_runner: CliRunner, edgedb: str) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "local",
            "scan",
            "--dsn",
            edgedb,
            *fixtures.folders,
        ],
    )
