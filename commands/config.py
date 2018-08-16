# -*- coding: utf-8 -*-
import click
from lib import helpers, database, server, persistence
from click_didyoumean import DYMGroup


@click.group(cls=DYMGroup)
@click.pass_context
def cli(ctx, **kwargs):
    '''Config management'''


@cli.command()
@helpers.coro
@click.pass_context
@helpers.add_options(persistence.options)
@helpers.add_options(database.options)
@helpers.add_options(server.options)
async def save(ctx, **kwargs):
    '''Save config'''
    redis = persistence.Persistence(**kwargs)
    await redis.connect()
    await redis.execute('set', 'my-key', 'value')
    val = await redis.execute('get', 'my-key')
    print(val)
    await redis.close()
