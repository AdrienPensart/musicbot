import click
import logging
from musicbot.lib import helpers, spotify

logger = logging.getLogger(__name__)


@click.group(cls=helpers.GroupWithHelp)
@helpers.add_options(spotify.options)
@click.pass_context
def cli(ctx, **kwargs):
    '''Spotify'''
    ctx.obj.sp = lambda: spotify.Spotify.new(**kwargs)


@cli.command()
@click.argument("artist")
@click.argument("title")
@click.pass_context
def track(ctx, artist, title):
    '''Search track'''
    print(ctx.obj.sp.search(artist, title))
