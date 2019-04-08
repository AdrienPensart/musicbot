import logging
import click
from musicbot import helpers
from musicbot.backend import database

logger = logging.getLogger(__name__)


@click.group(cls=helpers.GroupWithHelp)
def cli():
    '''Database management (admin)'''


@cli.command('cli', context_settings=dict(ignore_unknown_options=True))
@helpers.add_options(database.db_option)
@click.argument('pgcli_args', nargs=-1, type=click.UNPROCESSED)
def _pgcli(db, pgcli_args):
    '''Start PgCLI util'''
    from subprocess import call
    cmdline = ['pgcli', db] + list(pgcli_args)
    click.echo('Invoking: %s' % ' '.join(cmdline))
    call(cmdline)


@cli.command()
@helpers.add_options(database.db_option)
def create(**kwargs):
    '''Create database and load schema'''
    database.Database(**kwargs).create()


@cli.command()
@helpers.add_options(database.db_option)
@click.confirmation_option(help='Are you sure you want to drop the DB ?')
def drop(**kwargs):
    '''Drop database'''
    database.Database(**kwargs).drop()


@cli.command()
@helpers.add_options(database.db_option)
@click.confirmation_option(help='Are you sure you want to drop and recreate db?')
def clear(**kwargs):
    '''Drop and recreate database and schema'''
    database.Database(**kwargs).clear()
#
#
# @cli.command()
# @helpers.add_options(database.db_option)
# def stats(db):
#     '''Get stats about database'''
#     with psycopg2.connect(db) as con:
#         with con.cursor() as cur:
#             sql = '''SELECT relname,
#                             100 * idx_scan / nullif((seq_scan + idx_scan), 0) as percent_of_times_index_used,
#                             n_live_tup as rows_in_table
#                      FROM pg_stat_user_tables
#                      ORDER BY n_live_tup DESC'''
#             cur.execute(sql)
#             results = cur.fetchall()
#             for r in results:
#                 print(r)
#
#             # sql = '''SELECT query, total_time, calls, rows, total_time / calls as average_time, total_time / calls / nullif(rows, ?) as avg_row_time, ? * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, ?) AS cache_hit_percent FROM pg_stat_statements WHERE dbid = (select oid from pg_database where datname = current_database()) order by total_time desc limit 5'''
#             # cur.execute(sql)
#             # results = cur.fetchall()
#             # for r in results:
#             #     print(r)
