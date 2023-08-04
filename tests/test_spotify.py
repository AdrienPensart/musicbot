import logging

from beartype import beartype
from click.testing import CliRunner
from click_skeleton.testing import run_cli

from musicbot.main import cli
from musicbot.object import MusicbotObject

logger = logging.getLogger(__name__)


@beartype
def test_spotify_new_token(cli_runner: CliRunner) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "spotify",
            "new-token",
            "--dry",
        ],
    )


@beartype
def test_spotify_refresh_token(cli_runner: CliRunner) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "spotify",
            "new-token",
            "--dry",
        ],
    )


@beartype
def test_spotify_cached_token(cli_runner: CliRunner) -> None:
    _ = run_cli(cli_runner, cli, ["--quiet", "spotify", "cached-token"])


@beartype
def test_spotify_playlists(cli_runner: CliRunner) -> None:
    _ = run_cli(cli_runner, cli, ["--quiet", "spotify", "playlists"])


@beartype
def test_spotify_playlist(cli_runner: CliRunner) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "spotify",
            "playlist",
            "test",
        ],
    )


@beartype
def test_spotify_to_download(cli_runner: CliRunner) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "spotify",
            "to-download",
        ],
    )


@beartype
def test_spotify_tracks(cli_runner: CliRunner) -> None:
    _ = run_cli(cli_runner, cli, ["--quiet", "spotify", "tracks"])


@beartype
def test_spotify_artist_diff(cli_runner: CliRunner, edgedb: str) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "spotify",
            "artist-diff",
            "--dsn",
            edgedb,
        ],
    )


@beartype
def test_spotify_track_diff(cli_runner: CliRunner, edgedb: str) -> None:
    output = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "spotify",
            "track-diff",
            "--dsn",
            edgedb,
            "--min-threshold",
            50,
            "--output",
            "json",
        ],
    )
    assert MusicbotObject.loads_json(output) is not None
