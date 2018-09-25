import click
from lib import helpers, lib, database
from lib.collection import Collection


@click.group(cls=helpers.GroupWithHelp)
@helpers.add_options(database.options)
@helpers.coro
@click.pass_context
async def cli(ctx, **kwargs):
    '''Task management'''
    lib.raise_limits()
    ctx.obj.db = await Collection.make(**kwargs)


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
