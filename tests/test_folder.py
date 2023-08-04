from beartype import beartype
from click.testing import CliRunner
from click_skeleton.helpers import mysplit
from click_skeleton.testing import run_cli

from musicbot.main import cli

from . import fixtures


@beartype
def test_folder_find(cli_runner: CliRunner) -> None:
    musics = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "folder",
            "find",
            *fixtures.folders,
        ],
    )
    assert len(mysplit(musics, "\n")) == 5


@beartype
def test_folder_flac2mp3(cli_runner: CliRunner) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "folder",
            "flac2mp3",
            "--dry",
            *fixtures.folders,
        ],
    )


@beartype
def test_folder_playlist(cli_runner: CliRunner) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "folder",
            "playlist",
            *fixtures.folders,
        ],
    )


@beartype
def test_folder_issues(cli_runner: CliRunner) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "folder",
            "issues",
            *fixtures.folders,
        ],
    )


@beartype
def test_folder_manual_fix(cli_runner: CliRunner) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "folder",
            "manual-fix",
            *fixtures.folders,
            "--dry",
        ],
    )


@beartype
def test_folder_set_tags(cli_runner: CliRunner) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "folder",
            "set-tags",
            *fixtures.folders,
            "--dry",
        ],
    )


@beartype
def test_folder_add_keywords(cli_runner: CliRunner) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "folder",
            "add-keywords",
            *fixtures.folders,
            "--keywords",
            "test",
            "--dry",
        ],
    )


@beartype
def test_folder_delete_keywords(cli_runner: CliRunner) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "folder",
            "delete-keywords",
            *fixtures.folders,
            "--keywords",
            "test",
            "--dry",
        ],
    )
