import logging

import pytest
from beartype import beartype
from click.testing import CliRunner
from click_skeleton.testing import run_cli

from musicbot.main import cli
from musicbot.object import MusicbotObject

logger = logging.getLogger(__name__)


@pytest.mark.runner_setup(mix_stderr=False)
@beartype
def test_spotify_cached_token(cli_runner: CliRunner) -> None:
    run_cli(cli_runner, cli, ["--quiet", "spotify", "cached-token"])


@pytest.mark.runner_setup(mix_stderr=False)
@beartype
def test_spotify_playlists(cli_runner: CliRunner) -> None:
    run_cli(cli_runner, cli, ["--quiet", "spotify", "playlists"])


@pytest.mark.runner_setup(mix_stderr=False)
@beartype
def test_spotify_tracks(cli_runner: CliRunner) -> None:
    run_cli(cli_runner, cli, ["--quiet", "spotify", "tracks"])


@pytest.mark.runner_setup(mix_stderr=False)
@beartype
def test_spotify_artist_diff(cli_runner: CliRunner, edgedb: str) -> None:
    run_cli(
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


@pytest.mark.runner_setup(mix_stderr=False)
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
    _ = MusicbotObject.loads_json(output)
