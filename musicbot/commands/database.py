import logging
import subprocess
import webbrowser

import click
from beartype import beartype
from click_skeleton import AdvancedGroup

from musicbot.cli.musicdb import musicdb_options
from musicbot.cli.options import yes_option
from musicbot.helpers import syncify
from musicbot.musicdb import MusicDb
from musicbot.object import MusicbotObject


@click.group(help="DB management", cls=AdvancedGroup, aliases=["db"])
@beartype
def cli() -> None:
    pass


@cli.command(help="EdgeDB raw query", aliases=["query", "fetch", "execute"])
@click.argument("query")
@musicdb_options
@syncify
@beartype
async def edgeql(musicdb: MusicDb, query: str) -> None:
    print(await musicdb.query_json(query))


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
@click.argument("pgcli_args", nargs=-1, type=click.UNPROCESSED)
@musicdb_options
@click.pass_context
@beartype
def pgcli(ctx: click.Context, musicdb: MusicDb, pgcli_args: tuple[str, ...]) -> None:
    if "--help" in pgcli_args:
        MusicbotObject.echo(ctx.get_help())
        MusicbotObject.echo("\n")
    from pgcli.main import cli as pg_cli

    dsn = musicdb.dsn.replace("edgedb://", "postgresql://")
    args = [dsn] + list(pgcli_args)
    pgcli_logger = logging.getLogger("pgcli.main")
    pgcli_logger.setLevel(logging.ERROR)
    pg_cli.main(prog_name="pgcli", args=args)


@cli.command(help="Explore with GraphiQL")
@musicdb_options
@beartype
def graphiql(musicdb: MusicDb) -> None:
    if musicdb.graphql:
        url = f"{musicdb.graphql}/explore"
        MusicbotObject.success(url)
        if not MusicbotObject.dry:
            _ = webbrowser.open(url)


@cli.command(help="Explore with EdgeDB UI")
@beartype
def ui() -> None:
    args = ["edgedb", "ui", "--print-url", "--no-server-check"]
    try:
        _ = subprocess.run(args, check=True)
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
    await musicdb.clean_musics()


@cli.command(help="Clean entities without musics associated")
@musicdb_options
@syncify
@beartype
async def soft_clean(musicdb: MusicDb) -> None:
    await musicdb.soft_clean()
