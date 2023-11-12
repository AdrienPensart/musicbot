import logging
import subprocess
import webbrowser

import click
from beartype import beartype
from click_skeleton import AdvancedGroup

from musicbot import MusicbotObject, MusicDb, syncify
from musicbot.cli.musicdb import musicdb_options
from musicbot.cli.options import open_option, output_option, yes_option


@click.group(help="DB management", cls=AdvancedGroup, aliases=["db", "edgedb"])
@beartype
def cli() -> None:
    pass


@cli.command(help="EdgeDB raw query", aliases=["query", "fetch", "execute"])
@click.argument("query")
@musicdb_options
@output_option
@syncify
@beartype
async def edgeql(musicdb: MusicDb, output: str, query: str) -> None:
    result = await musicdb.query_json(query)
    if output == "json":
        intermediate_json = MusicbotObject.loads_json(result)
        if intermediate_json is not None:
            MusicbotObject.print_json(intermediate_json)
    else:
        print(result)


@cli.command(help="GraphQL query")
@click.argument("query")
@musicdb_options
@syncify
@beartype
async def graphql(musicdb: MusicDb, query: str) -> None:
    response = await musicdb.graphql_query(query)
    if response is not None:
        MusicbotObject.print_json(response.json())


@cli.command(help="Connect with PgCLI", context_settings=dict(ignore_unknown_options=True, help_option_names=[]))
@click.pass_context
@click.argument("pgcli_args", nargs=-1, type=click.UNPROCESSED)
@musicdb_options
@beartype
def pgcli(ctx: click.Context, musicdb: MusicDb, pgcli_args: tuple[str, ...]) -> None:
    if "--help" in pgcli_args:
        MusicbotObject.echo(ctx.get_help())
        MusicbotObject.echo("\n")
    from pgcli.main import cli as pg_cli

    dsn = musicdb.dsn.replace("edgedb://", "postgresql://")
    dsn += "/edgedb"
    args = [dsn] + list(pgcli_args)
    pgcli_logger = logging.getLogger("pgcli.main")
    pgcli_logger.setLevel(logging.ERROR)
    MusicbotObject.success(f"Connecting to : {dsn}")
    pg_cli.main(prog_name="pgcli", args=args)


@cli.command(help="Explore with GraphiQL")
@musicdb_options
@open_option
@beartype
def graphiql(musicdb: MusicDb, _open: bool) -> None:
    if musicdb.graphql:
        print(musicdb.graphiql)
        if _open and not MusicbotObject.dry:
            _ = webbrowser.open(musicdb.graphiql)


@cli.command(help="Explore with EdgeDB UI", context_settings=dict(ignore_unknown_options=True, help_option_names=[]))
@click.pass_context
@click.argument("edgedb_args", nargs=-1, type=click.UNPROCESSED)
@open_option
@musicdb_options
@beartype
def ui(
    ctx: click.Context,
    musicdb: MusicDb,
    _open: bool,
    edgedb_args: tuple[str, ...],
) -> None:
    if "--help" in edgedb_args:
        MusicbotObject.echo(ctx.get_help())
        MusicbotObject.echo("\n")

    args = ["edgedb", "ui", "--print-url", "--no-server-check", "--dsn", musicdb.dsn] + list(edgedb_args)
    try:
        url = subprocess.check_output(
            " ".join(args),
            stderr=subprocess.STDOUT,
            shell=True,
            text=True,
        ).strip()
        print(url)
        if _open and not MusicbotObject.dry:
            _ = webbrowser.open(url)
    except FileNotFoundError:
        MusicbotObject.err("Unable to locate edgedb CLI, please install it first with")
        MusicbotObject.tip("curl --proto '=https' --tlsv1.2 -sSf https://sh.edgedb.com | sh")
    except subprocess.CalledProcessError as error:
        joined_args = " ".join(args)
        MusicbotObject.err(f"Failed to run : {joined_args}", error=error)


@cli.command(help="Clean all musics in DB", aliases=["clean-db", "erase"])
@musicdb_options
@yes_option
@syncify
@beartype
async def clean(musicdb: MusicDb) -> None:
    _ = await musicdb.clean_musics()


@cli.command(help="Drop entire schema from DB")
@musicdb_options
@yes_option
@syncify
@beartype
async def drop(musicdb: MusicDb) -> None:
    _ = await musicdb.drop()


@cli.command(help="Clean entities without musics associated")
@musicdb_options
@syncify
@beartype
async def soft_clean(musicdb: MusicDb) -> None:
    _ = await musicdb.soft_clean()
