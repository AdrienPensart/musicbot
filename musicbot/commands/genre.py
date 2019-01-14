import logging
import click
from musicbot import helpers, user

logger = logging.getLogger(__name__)


@click.group(cls=helpers.GroupWithHelp)
@click.pass_context
@helpers.add_options(user.auth_options)
def cli(ctx, **kwargs):
    '''Genre management'''
    ctx.obj.u = lambda: user.User.new(**kwargs)


@cli.command('list')
@click.pass_context
def _list(ctx):
    '''List genres'''
    for g in ctx.obj.u().genres:
        print(g)
