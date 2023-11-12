import httpx
from beartype import beartype
from click.testing import CliRunner
from click_skeleton.testing import run_cli

from musicbot.main import cli
from musicbot.object import MusicbotObject


@beartype
def test_database_pgcli(cli_runner: CliRunner, edgedb: str) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "database",
            "pgcli",
            "--dsn",
            edgedb,
        ],
    )


@beartype
def test_database_edgeql(cli_runner: CliRunner, edgedb: str) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "database",
            "execute",
            "select Music;",
            "--dsn",
            edgedb,
        ],
    )


@beartype
def test_database_graphql(cli_runner: CliRunner, edgedb: str) -> None:
    output = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "database",
            "graphql",
            "test",
            "--dsn",
            edgedb,
        ],
    )
    assert MusicbotObject.loads_json(output) is not None


@beartype
def test_database_graphiql(cli_runner: CliRunner, edgedb: str) -> None:
    url = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "database",
            "graphiql",
            "--dsn",
            edgedb,
            "--no-open",
        ],
    )
    _ = httpx.head(url, timeout=5)


@beartype
def test_database_ui(cli_runner: CliRunner, edgedb: str) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "database",
            "ui",
            "--dsn",
            edgedb,
            "--no-open",
        ],
    )


@beartype
def test_database_clean(cli_runner: CliRunner, edgedb: str) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "database",
            "clean",
            "--dsn",
            edgedb,
            "--yes",
        ],
    )


@beartype
def test_database_drop(cli_runner: CliRunner, edgedb: str) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "--dry",
            "database",
            "drop",
            "--dsn",
            edgedb,
            "--yes",
        ],
    )


@beartype
def test_database_soft_clean(cli_runner: CliRunner, edgedb: str) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "database",
            "soft-clean",
            "--dsn",
            edgedb,
        ],
    )
