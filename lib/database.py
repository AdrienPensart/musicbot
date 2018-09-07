import click
import os
import sys
import logging
from asyncpg import utils, connect
from .helpers import drier
from .config import config

logger = logging.getLogger(__name__)

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 5432
DEFAULT_DATABASE = 'musicbot_prod'
DEFAULT_USER = 'postgres'
DEFAULT_PASSWORD = 'musicbot'

options = [
    click.option('--db-host', envvar='MB_DB_HOST', help='DB host', default=DEFAULT_HOST, show_default=True),
    click.option('--db-port', envvar='MB_DB_PORT', help='DB port', default=DEFAULT_PORT, show_default=True),
    click.option('--db-database', envvar='MB_DATABASE', help='DB name', default=DEFAULT_DATABASE, show_default=True),
    click.option('--db-user', envvar='MB_DB_USER', help='DB user', default=DEFAULT_USER, show_default=True),
    click.option('--db-password', envvar='MB_DB_PASSWORD', help='DB password', default=DEFAULT_PASSWORD, show_default=True)
]


class Database:
    def __init__(self, max_conn=100, **kwargs):
        self.set(**kwargs)
        self.max_conn = max_conn

    def set(self, db_host=None, db_port=None, db_database=None, db_user=None, db_password=None):
        self.host = db_host or os.getenv('MB_DB_HOST', DEFAULT_HOST)
        self.port = db_port or os.getenv('MB_DB_PORT', str(DEFAULT_PORT))
        self.database = db_database or os.getenv('MB_DATABASE', DEFAULT_DATABASE)
        self.user = db_user or os.getenv('MB_DB_USER', DEFAULT_USER)
        self.password = db_password or os.getenv('MB_DB_PASSWORD', DEFAULT_PASSWORD)
        self._pool = None
        logger.info('Database: %s', self.connection_string)

    @property
    def connection_string(self):
        return 'postgresql://{}:{}@{}:{}/{}'.format(self.user, self.password, self.host, self.port, self.database)

    async def close(self):
        await (await self.pool).close()

    def __str__(self):
        return self.connection_string

    async def mogrify(self, connection, sql, *args):
        mogrified = await utils._mogrify(connection, sql, args)
        logger.debug('mogrified: %s', mogrified)

    @drier
    async def dropdb(self):
        con = await connect(user=self.user, host=self.host, password=self.password, port=self.port)
        await con.execute('drop database if exists {}'.format(self.database))
        await con.close()

    @drier
    async def createdb(self):
        con = await connect(user=self.user, host=self.host, password=self.password, port=self.port)
        # as postgresql does not support "create database if not exists", need to check in catalog
        result = await con.fetchrow("select count(*) = 0 as not_exists from pg_catalog.pg_database where datname = '{}'".format(self.database))
        if result['not_exists']:
            logger.debug('Database does not exists, create it')
            await con.execute('create database {}'.format(self.database))
        else:
            logger.debug('Database already exists.')
        await con.close()

    async def connect(self):
        return await connect(user=self.user, host=self.host, password=self.password, port=self.port, database=self.database)

    @property
    async def pool(self):
        if self._pool is None:
            import asyncpg

            async def add_log_listener(conn):
                def log_it(conn, message):
                    logger.debug(message)
                if config.debug:
                    conn.add_log_listener(log_it)
            self._pool: asyncpg.pool.Pool = await asyncpg.create_pool(max_size=self.max_conn, user=self.user, host=self.host, password=self.password, port=self.port, database=self.database, setup=add_log_listener)
        return self._pool

    async def fetch(self, sql, *args):
        if config.debug:
            async with (await self.pool).acquire() as connection:
                await self.mogrify(connection, sql, *args)
                return await connection.fetch(sql, *args)
        return await (await self.pool).fetch(sql, *args)

    async def fetchrow(self, sql, *args):
        if config.debug:
            async with (await self.pool).acquire() as connection:
                await self.mogrify(connection, sql, *args)
                return await connection.fetchrow(sql, *args)
        return await (await self.pool).fetchrow(sql, *args)

    @drier
    async def executefile(self, filepath):
        schema_path = os.path.join(os.path.dirname(sys.argv[0]), filepath)
        logger.info('loading schema: %s', schema_path)
        with open(schema_path, "r") as s:
            sql = s.read()
            if config.debug:
                async with (await self.pool).acquire() as connection:
                    async with connection.transaction():
                        return await connection.execute(sql)
            await (await self.pool).execute(sql)

    @drier
    async def execute(self, sql, *args):
        if config.debug:
            async with (await self.pool).acquire() as connection:
                async with connection.transaction():
                    await self.mogrify(connection, sql, *args)
                    return await connection.execute(sql, *args)
        return await (await self.pool).execute(sql, *args)

    @drier
    async def executemany(self, sql, *args, **kwargs):
        if config.debug:
            async with (await self.pool).acquire() as connection:
                async with connection.transaction():
                    return await connection.executemany(sql, *args, **kwargs)
        return await (await self.pool).executemany(sql, *args, **kwargs)
