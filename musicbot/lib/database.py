import logging
import click
import psycopg2
import os
from psycopg2.extensions import parse_dsn

logger = logging.getLogger(__name__)

DEFAULT_DB = 'postgresql://postgres:musicbot@localhost:5432/musicbot_prod'
DEFAULT_DB_MAX = 32
DEFAULT_DB_SINGLE = False
DEFAULT_DB_CERT = '~/.postgresql/root.crt'

MB_DB = 'MB_DB'
MB_DB_MAX = 'MB_DB_MAX'
MB_DB_SINGLE = 'MB_DB_SINGLE'
MB_DB_CERT = 'MB_DB_CERT'

db_option = [click.option('--db', envvar=MB_DB, help='DB dsn string', default=DEFAULT_DB, show_default=True)]

options = [
    db_option,
    click.option('--db-max', envvar=MB_DB_MAX, help='DB maximum number of connections', default=DEFAULT_DB_MAX, show_default=True),
    click.option('--db-single', envvar=MB_DB_SINGLE, help='DB will use only one connection', default=DEFAULT_DB_SINGLE, is_flag=True, show_default=True),
    click.option('--db-cert', envvar=MB_DB_CERT, help='DB SSL certificate', default=DEFAULT_DB_CERT, show_default=True)
]


def create(db):
    params = parse_dsn(db)
    db_to_create = params['dbname']
    del params['dbname']

    with psycopg2.connect(**params) as con:
        con.autocommit = True
        with con.cursor() as cur:
            cur.execute("select count(*) = 1 from pg_catalog.pg_database where datname = '{}'".format(db_to_create))
            result = cur.fetchone()
            if not result[0]:
                logger.debug('Database %s does not exists, create it', db_to_create)
                cur.execute('create database {}'.format(db_to_create))
            else:
                logger.debug('Database %s already exists', db_to_create)

    params['dbname'] = db_to_create
    with psycopg2.connect(**params) as con:
        with con.cursor() as cur:
            for sqlfile in ['schemas.sql', 'extensions.sql', 'user.sql', 'raw_music.sql', 'filter.sql', 'playlist.sql', 'stat.sql']:
                script = os.path.join(os.path.dirname(__file__), '../schema/', sqlfile)
                logger.debug('Loading %s', script)
                content = open(script).read()
                cur.execute(content)
        con.commit()


def drop(db):
    params = parse_dsn(db)
    db_to_drop = params['dbname']
    del params['dbname']
    con = psycopg2.connect(**params)
    con.autocommit = True
    cur = con.cursor()
    cur.execute('''
        select pg_terminate_backend(pg_stat_activity.pid)
        from pg_stat_activity
        where pg_stat_activity.datname = '{}' and pid <> pg_backend_pid()'''.format(db_to_drop))
    cur.execute('drop schema if exists musicbot_private cascade')
    cur.execute('drop schema if exists musicbot_public cascade')
    cur.execute('drop database if exists {}'.format(db_to_drop))


def clear(db):
    drop(db)
    create(db)
