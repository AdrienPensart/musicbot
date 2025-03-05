import httpx
from beartype import beartype
from click.testing import CliRunner
from click_skeleton.testing import run_cli

from musicbot.main import cli
from musicbot.object import MusicbotObject


@beartype
def test_database_pgcli(cli_runner: CliRunner, dsn: str) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "database",
            "pgcli",
            "--dsn",
            dsn,
        ],
    )


@beartype
def test_database_edgeql(cli_runner: CliRunner, dsn: str) -> None:
    output = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "database",
            "execute",
            "select Music;",
            "--dsn",
            dsn,
            "--output",
            "json",
        ],
    )
    assert MusicbotObject.loads_json(output) is not None, output


@beartype
def test_database_graphql(cli_runner: CliRunner, dsn: str) -> None:
    output = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "database",
            "graphql",
            "test",
            "--dsn",
            dsn,
        ],
    )
    assert MusicbotObject.loads_json(output) is not None, output


@beartype
def test_database_graphiql(cli_runner: CliRunner, dsn: str) -> None:
    url = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "database",
            "graphiql",
            "--dsn",
            dsn,
            "--no-open",
        ],
    )
    _ = httpx.get(url, timeout=5, verify=False)


@beartype
def test_database_ui(cli_runner: CliRunner, dsn: str) -> None:
    url = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "database",
            "ui",
            "--dsn",
            dsn,
            "--no-open",
        ],
    )
    _ = httpx.get(url, timeout=5, verify=False)


@beartype
def test_database_clean(cli_runner: CliRunner, dsn: str) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "database",
            "clean",
            "--dsn",
            dsn,
            "--yes",
        ],
    )


@beartype
def test_database_drop(cli_runner: CliRunner, dsn: str) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "--dry",
            "database",
            "drop",
            "--dsn",
            dsn,
            "--yes",
        ],
    )


@beartype
def test_database_soft_clean(cli_runner: CliRunner, dsn: str) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "database",
            "soft-clean",
            "--dsn",
            dsn,
        ],
    )
