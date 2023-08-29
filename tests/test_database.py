from beartype import beartype
from click.testing import CliRunner
from click_skeleton.testing import run_cli

from musicbot.main import cli


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
    _ = run_cli(
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


@beartype
def test_database_graphiql(cli_runner: CliRunner, edgedb: str) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "database",
            "graphiql",
            "--dsn",
            edgedb,
        ],
    )


@beartype
def test_database_ui(cli_runner: CliRunner) -> None:
    _ = run_cli(
        cli_runner,
        cli,
        [
            "--quiet",
            "database",
            "ui",
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
