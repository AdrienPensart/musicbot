import click
import logging
import json
from musicbot.lib import helpers, user, mfilter

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
    ctx.obj.u().load_default_filters()


@cli.command()
@click.pass_context
def list(ctx):
    print(json.dumps(ctx.obj.u().filters))


@cli.command()
@helpers.add_options(mfilter.options)
@click.pass_context
def do(ctx, **kwargs):
    mf = mfilter.Filter(**kwargs)
    print(json.dumps(ctx.obj.u().do_filter(mf)))


@cli.command()
@click.pass_context
@click.argument('name')
def get(ctx, name):
    print(json.dumps(ctx.obj.u().filter(name)))
