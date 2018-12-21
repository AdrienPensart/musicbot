import logging
import click
import psycopg2
import os
from psycopg2.extensions import parse_dsn

logger = logging.getLogger(__name__)

DEFAULT_DB = 'postgresql://postgres:musicbot@localhost:5432/musicbot_prod'
MB_DB = 'MB_DB'

db_option = [click.option('--db', envvar=MB_DB, help='DB dsn string', default=DEFAULT_DB, show_default=True)]


class Database:
    def __init__(self, db=None):
        self.db = db if db is not None else os.getenv(MB_DB, DEFAULT_DB)

    def create(self):
        params = parse_dsn(self.db)
        db_to_create = params['dbname']
        del params['dbname']

        with psycopg2.connect(**params) as con:
            con.autocommit = True
            with con.cursor() as cur:
                cur.execute("select count(*) = 1 from pg_catalog.pg_database where datname = '{}'".format(db_to_create))
                result = cur.fetchone()
                logger.debug('Database exists? : %s', result[0])
                if not result[0]:
                    cur.execute('create database {}'.format(db_to_create))

        params['dbname'] = db_to_create
        with psycopg2.connect(**params) as con:
            with con.cursor() as cur:
                for sqlfile in ['schemas.sql', 'extensions.sql', 'user.sql', 'raw_music.sql', 'filter.sql', 'playlist.sql', 'stat.sql']:
                    script = os.path.join(os.path.dirname(__file__), '../schema/', sqlfile)
                    logger.debug('Loading %s', script)
                    content = open(script).read()
                    cur.execute(content)
            con.commit()

    def drop(self):
        params = parse_dsn(self.db)
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

    def clear(self):
        self.drop()
        self.create()
