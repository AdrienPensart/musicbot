import click
import os
import logging
from lib import helpers, database, collection

logger = logging.getLogger(__name__)


@click.group(cls=helpers.GroupWithHelp)
@helpers.add_options(database.options)
@click.pass_context
def cli(ctx, **kwargs):
    '''Database management'''
    ctx.obj.db = collection.Collection(**kwargs)
    logger.info(ctx.obj.db.connection_string)


@cli.command()
@helpers.coro
@click.pass_context
async def create(ctx):
    '''Create database and load schema'''
    await ctx.obj.db.create(os.path.join(ctx.obj.folder, 'schema'))


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
    await ctx.obj.db.clear(os.path.join(ctx.obj.folder, 'schema'))


@cli.command()
@helpers.coro
@click.pass_context
async def clean(ctx):
    '''Clean deleted musics from database'''
    musics = await ctx.obj.db.musics()
    for m in musics:
        if not os.path.isfile(m['path']):
            logger.info('%s does not exist', m['path'])
            await ctx.obj.db.delete(m['path'])
    await ctx.obj.db.refresh()


@cli.command()
@helpers.coro
@click.pass_context
async def refresh(ctx):
    '''Refresh database materialized views'''
    await ctx.obj.db.refresh()
