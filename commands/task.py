import click
from lib import helpers, lib, collection, database


@click.group(cls=helpers.GroupWithHelp)
@helpers.add_options(database.options)
@click.pass_context
def cli(ctx, **kwargs):
    '''Task management'''
    lib.raise_limits()
    ctx.obj.db = collection.Collection(**kwargs)


@cli.command()
@helpers.coro
@click.argument('name')
@click.pass_context
async def new(name):
    '''Add a new task in database'''
    print('task name:', name)


@cli.command('list')
@helpers.coro
@click.pass_context
async def ls():
    '''List tasks in database'''
