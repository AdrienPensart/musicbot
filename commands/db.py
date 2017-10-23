# -*- coding: utf-8 -*-
import click
from logging import debug, info
from lib import helpers


@click.group(invoke_without_command=False)
@helpers.add_options(helpers.db_options)
@click.pass_context
def cli(ctx, host, port, user, password, db, **kwargs):
    debug('db cli')
    db = helpers.DbContext(host=host, port=port, user=user, password=password, database=db)
    info(db.connection_string())
    ctx.obj.db = db


@cli.command()
@helpers.coro
@click.pass_context
async def create(ctx, **kwargs):
    await ctx.obj.db.create()


@cli.command()
@helpers.coro
@click.pass_context
async def drop(ctx, **kwargs):
    await ctx.obj.db.drop()


@cli.command()
@helpers.coro
@click.pass_context
async def clear(ctx, **kwargs):
    await ctx.obj.db.clear()


@cli.command()
@helpers.coro
@click.pass_context
async def clean(ctx, **kwargs):
    debug('clean')
    # for m in self.musics:
    # if(not os.path.isfile(m.path)):
    #     info('{} does not exist'.format(m.path))
    #     self.collection.delete(m.path)
