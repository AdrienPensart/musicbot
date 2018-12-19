import datetime
import click
from musicbot import lib, helpers, user
from musicbot.music import mfilter


@click.group(cls=helpers.GroupWithHelp)
@click.pass_context
@helpers.add_options(user.auth_options)
def cli(ctx, **kwargs):
    '''Youtube management'''
    ctx.obj.u = lambda: user.User.new(**kwargs)


@cli.command()
@click.pass_context
@helpers.add_options(mfilter.options)
def show(ctx, **kwargs):
    '''Generate some stats for music collection with filters'''
    mf = mfilter.Filter(**kwargs)
    stats = ctx.obj.u().do_stat(mf)
    print("Music    :", stats['musics'])
    print("Artist   :", stats['artists'])
    print("Album    :", stats['albums'])
    print("Genre    :", stats['genres'])
    print("Keywords :", stats['keywords'])
    print("Size     :", lib.bytes_to_human(int(stats['size'])))
    print("Total duration :", datetime.timedelta(seconds=int(stats['duration'])))
