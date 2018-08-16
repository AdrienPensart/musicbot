# -*- coding: utf-8 -*-
import click
from lib import helpers, lib, collection, database
from click_didyoumean import DYMGroup


@click.group(invoke_without_command=False, cls=DYMGroup)
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
async def new(ctx, name, **kwargs):
    '''Add a new task in database'''
    print('task name:', name)


@cli.command()
@helpers.coro
@click.pass_context
async def list(ctx, **kwargs):
    '''List tasks in database'''
