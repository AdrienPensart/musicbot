# -*- coding: utf-8 -*-
import click
import os
from logging import info
from lib import helpers, database


@click.group()
@helpers.add_options(database.options)
@click.pass_context
def cli(ctx, **kwargs):
    '''Database management'''
    db = database.DbContext(**kwargs)
    info(db.connection_string())
    ctx.obj.db = db


@cli.command()
@helpers.coro
@click.pass_context
async def create(ctx):
    '''Create database and load schema'''
    await ctx.obj.db.create()


@cli.command()
@helpers.coro
@click.confirmation_option(help='Are you sure you want to drop the db?')
@click.pass_context
async def drop(ctx):
    '''Drop database schema'''
    await ctx.obj.db.drop()


@cli.command()
@helpers.coro
@click.confirmation_option(help='Are you sure you want to drop the db?')
@click.pass_context
async def clear(ctx):
    '''Drop and recreate database and schema'''
    await ctx.obj.db.clear()


@cli.command()
@helpers.coro
@click.pass_context
async def clean(ctx):
    '''Clean deleted musics from database'''
    musics = await ctx.obj.db.filter()
    for m in musics:
        if not os.path.isfile(m['path']):
            info('{} does not exist'.format(m['path']))
            await ctx.obj.db.delete(m['path'])
