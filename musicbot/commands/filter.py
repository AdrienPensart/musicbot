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
    ctx.obj.u = user.User(**kwargs)


@cli.command()
@helpers.add_options(mfilter.options)
@click.pass_context
def default(ctx):
    ctx.obj.u.default_filters()


@cli.command()
@helpers.add_options(mfilter.options)
@click.pass_context
def do(ctx, **kwargs):
    mf = mfilter.Filter(**kwargs)
    print(json.dumps(ctx.obj.u.do_filter(mf)))
