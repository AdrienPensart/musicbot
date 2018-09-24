import click
import os
import logging
from lib import helpers, database, collection

logger = logging.getLogger(__name__)


@click.group(cls=helpers.GroupWithHelp)
@click.pass_context
def cli(ctx):
    '''Database management'''


@cli.command('cli')
@helpers.add_options(database.options)
def pgcli(**kwargs):
    '''Start PgCLI util'''
    db = collection.Collection(**kwargs)
    os.system(r"pgcli {}".format(db.connection_string))


@cli.command()
@helpers.coro
@click.pass_context
@helpers.add_options(database.options)
async def create(ctx, **kwargs):
    '''Create database and load schema'''
    db = collection.Collection(**kwargs)
    await db.create()


@cli.command()
@helpers.coro
@helpers.add_options(database.options)
@click.confirmation_option(help='Are you sure you want to drop the DB ?')
async def drop(**kwargs):
    '''Drop database schema'''
    db = collection.Collection(**kwargs)
    await db.drop()


@cli.command()
@helpers.coro
@helpers.add_options(database.options)
@click.confirmation_option(help='Are you sure you want to drop all objects in DB ?')
async def empty(**kwargs):
    db = collection.Collection(**kwargs)
    await db.empty()


@cli.command()
@helpers.coro
@helpers.add_options(database.options)
@click.confirmation_option(help='Are you sure you want to drop the db?')
@click.pass_context
async def clear(ctx, **kwargs):
    '''Drop and recreate database and schema'''
    db = collection.Collection(**kwargs)
    await db.clear(os.path.join(ctx.obj.folder, 'schema'))


@cli.command()
@helpers.coro
@helpers.add_options(database.options)
async def clean(**kwargs):
    '''Clean deleted musics from database'''
    db = collection.Collection(**kwargs)
    musics = await db.musics()
    for m in musics:
        if not os.path.isfile(m['path']):
            logger.info('%s does not exist', m['path'])
            await db.delete(m['path'])
    await db.refresh()


@cli.command()
@helpers.coro
@helpers.add_options(database.options)
async def refresh(**kwargs):
    '''Refresh database materialized views'''
    db = collection.Collection(**kwargs)
    await db.refresh()


@cli.command()
@helpers.coro
@helpers.add_options(database.options)
async def stats(**kwargs):
    '''Get stats about database'''
    db = collection.Collection(**kwargs)
    sql = '''SELECT relname,
                    100 * idx_scan / nullif((seq_scan + idx_scan), 0) as percent_of_times_index_used,
                    n_live_tup as rows_in_table
             FROM pg_stat_user_tables
             ORDER BY n_live_tup DESC;'''
    results = await db.fetch(sql)
    for r in results:
        print(r)
    sql = '''SELECT query, total_time, calls, rows, total_time / calls as average_time, total_time / calls / nullif(rows, ?) as avg_row_time, ? * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, ?) AS cache_hit_percent FROM pg_stat_statements WHERE dbid = (select oid from pg_database where datname = current_database()) ORDER BY total_time DESC LIMIT ?'''
    results = await db.fetch(sql)
    for r in results:
        print(r)
