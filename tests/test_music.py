from beartype import beartype
from click.testing import CliRunner
from click_skeleton.testing import run_cli

from musicbot.main import cli

from . import fixtures


@beartype
def test_music_flac2mp3(cli_runner: CliRunner) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "music",
            "flac2mp3",
            str(fixtures.folder_flac),
            str(fixtures.one_flac),
            "/tmp",
        ],
    )


@beartype
def test_music_show(cli_runner: CliRunner) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "music",
            "show",
            str(fixtures.folder_flac),
            str(fixtures.one_flac),
        ],
    )


@beartype
def test_music_shazam(cli_runner: CliRunner) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "music",
            "shazam",
            str(fixtures.folder_flac),
            str(fixtures.one_flac),
        ],
    )

    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "music",
            "shazam",
            str(fixtures.folder_mp3),
            str(fixtures.one_mp3),
        ],
    )


@beartype
def test_music_fingerprint(cli_runner: CliRunner) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "music",
            "fingerprint",
            str(fixtures.folder_flac),
            str(fixtures.one_flac),
        ],
    )

    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "music",
            "fingerprint",
            str(fixtures.folder_mp3),
            str(fixtures.one_mp3),
        ],
    )


@beartype
def test_music_manual_fix(cli_runner: CliRunner) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "music",
            "manual-fix",
            str(fixtures.folder_flac),
            str(fixtures.one_flac),
        ],
    )

    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "music",
            "manual-fix",
            str(fixtures.folder_mp3),
            str(fixtures.one_mp3),
        ],
    )


@beartype
def test_music_tags(cli_runner: CliRunner) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "music",
            "tags",
            str(fixtures.folder_flac),
            str(fixtures.one_flac),
        ],
    )
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "music",
            "tags",
            str(fixtures.folder_mp3),
            str(fixtures.one_mp3),
        ],
    )


@beartype
def test_music_set_tags(cli_runner: CliRunner) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "music",
            "set-tags",
            str(fixtures.one_flac),
            "--rating",
            0,
            "--dry",
        ],
    )
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "music",
            "set-tags",
            str(fixtures.one_mp3),
            "--rating",
            0,
            "--dry",
        ],
    )


@beartype
def test_music_replace_keyword(cli_runner: CliRunner) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "music",
            "replace-keyword",
            str(fixtures.folder_flac),
            str(fixtures.one_flac),
            "to-replace",
            "replaced",
            "--dry",
        ],
    )


@beartype
def test_music_issues(cli_runner: CliRunner) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "music",
            "issues",
            str(fixtures.folder_flac),
            str(fixtures.one_flac),
        ],
    )
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "music",
            "issues",
            str(fixtures.folder_mp3),
            str(fixtures.one_mp3),
        ],
    )


@beartype
def test_music_add_keywords(cli_runner: CliRunner) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "music",
            "add-keywords",
            str(fixtures.folder_flac),
            str(fixtures.one_flac),
            "test",
            "--dry",
        ],
    )
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "music",
            "add-keywords",
            str(fixtures.folder_mp3),
            str(fixtures.one_mp3),
            "test",
            "--dry",
        ],
    )


@beartype
def test_music_delete_keywords(cli_runner: CliRunner) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "music",
            "delete-keywords",
            str(fixtures.folder_flac),
            str(fixtures.one_flac),
            "test",
            "--dry",
        ],
    )
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "music",
            "delete-keywords",
            str(fixtures.folder_mp3),
            str(fixtures.one_mp3),
            "test",
            "--dry",
        ],
    )
