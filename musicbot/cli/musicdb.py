import click
from click_option_group import optgroup  # type: ignore
from click_skeleton import add_options
from edgedb.blocking_client import create_client

from musicbot.cli.options import config_string
from musicbot.musicdb import MusicDb


def sane_musicdb(ctx: click.Context, param: click.Parameter, value: str) -> MusicDb:
    if param.name:
        ctx.params[param.name] = value
    dsn = ctx.params.pop('dsn')
    client = create_client(dsn=dsn)
    musicdb = MusicDb(client)
    ctx.params['musicdb'] = musicdb
    return musicdb


musicdb_options = add_options(
    optgroup('MusicDB options'),
    optgroup.option(
        '--dsn',
        help='DSN to MusicBot EdgeDB',
        callback=config_string,
    ),
    optgroup.option(
        '--musicdb',
        expose_value=False,
        callback=sane_musicdb,
    ),
)
