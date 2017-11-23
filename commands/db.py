# -*- coding: utf-8 -*-
import click
import os
from logging import info
from lib import options, helpers, database


@click.group()
@options.add_options(options.db)
@click.pass_context
def cli(ctx, **kwargs):
    '''Database management'''
    db = database.DbContext(**kwargs)
    info(db.connection_string())
    ctx.obj.db = db


@cli.command()
@helpers.coro
@click.pass_context
async def create(ctx, **kwargs):
    '''Create database and load schema'''
    await ctx.obj.db.create()


@cli.command()
@helpers.coro
@click.pass_context
async def drop(ctx, **kwargs):
    '''Drop database schema'''
    await ctx.obj.db.drop()


@cli.command()
@helpers.coro
@click.pass_context
async def clear(ctx, **kwargs):
    '''Drop and recreate database and schema'''
    await ctx.obj.db.clear()


@cli.command()
@helpers.coro
@click.pass_context
async def clean(ctx, **kwargs):
    '''Clean deleted musics from database'''
    musics = await ctx.obj.db.filter()
    for m in musics:
        if not os.path.isfile(m['path']):
            info('{} does not exist'.format(m['path']))
            await ctx.obj.db.delete(m['path'])
