import logging
import json
import click
from musicbot import helpers, user
from musicbot.music import mfilter

logger = logging.getLogger(__name__)


@click.group(cls=helpers.GroupWithHelp)
@helpers.add_options(user.auth_options)
@click.pass_context
def cli(ctx, **kwargs):
    '''Filter management'''
    ctx.obj.u = lambda: user.User.new(**kwargs)


@cli.command()
@click.pass_context
def load_default(ctx):
    '''Load default filters'''
    ctx.obj.u().load_default_filters()


@cli.command('list')
@click.pass_context
def _list(ctx):
    '''List filters'''
    for f in ctx.obj.u().filters:
        print(f)


@cli.command()
@helpers.add_options(mfilter.options)
@click.pass_context
def do(ctx, **kwargs):
    '''Filter music'''
    mf = mfilter.Filter(**kwargs)
    print(json.dumps(ctx.obj.u().do_filter(mf)))


@cli.command()
@click.pass_context
@click.argument('name')
def get(ctx, name):
    '''Print a filter'''
    print(json.dumps(ctx.obj.u().filter(name)))
