import os
import sys
import logging
import ssl

import click
import asyncpg

from . import lib
from .helpers import drier
from .config import config

logger = logging.getLogger(__name__)

DEFAULT_DB = 'postgresql://postgres:musicbot@localhost:5432/musicbot_prod'
DEFAULT_DB_MAX = 32
DEFAULT_DB_SINGLE = False
DEFAULT_DB_CERT = '~/.postgresql/root.crt'

MB_DB = 'MB_DB'
MB_DB_MAX = 'MB_DB_MAX'
MB_DB_SINGLE = 'MB_DB_SINGLE'
MB_DB_CERT = 'MB_DB_CERT'

options = [
    click.option('--db', envvar=MB_DB, help='DB dsn string', default=DEFAULT_DB, show_default=True),
    click.option('--db-max', envvar=MB_DB_MAX, help='DB maximum number of connections', default=DEFAULT_DB_MAX, show_default=True),
    click.option('--db-single', envvar=MB_DB_SINGLE, help='DB will use only one connection', default=DEFAULT_DB_SINGLE, show_default=True),
    click.option('--db-cert', envvar=MB_DB_CERT, help='DB SSL certificate', default=DEFAULT_DB_CERT, show_default=True)
]


class Database:
    def __init__(self, **kwargs):
        self._pool = None
        self._conn = None
        self._ssl = None
        self.set(**kwargs)

    def set(self, db=None, db_max=None, db_single=None, db_cert=None):
        self.connection_string = db if db is not None else os.getenv(MB_DB, DEFAULT_DB)
        self.max = db_max if db_max is not None else int(os.getenv(MB_DB_MAX, str(DEFAULT_DB_MAX)))
        self.single = db_single if db_single is not None else lib.str2bool(os.getenv(MB_DB_SINGLE, str(DEFAULT_DB_SINGLE)))
        self.cert = db_cert if db_cert is not None else os.getenv(MB_DB_CERT, DEFAULT_DB_CERT)

        if os.path.isfile(self.cert):
            self._ssl = ssl.create_default_context(cafile=self.cert)
        logger.info('Database: %s (single: %s | connections: %s | cert: %s)', self.connection_string, self.single, self.max, self.cert)

    async def close(self):
        if self._pool is not None:
            await self._pool.close()
            self._pool = None
        if self._conn is not None:
            Database._remove_log_listener(self._conn)
            await self._conn.close()
            self._conn = None

    def __str__(self):
        return self.connection_string

    async def mogrify(self, connection, sql, *args):
        mogrified = await asyncpg.utils._mogrify(connection, sql, args)  # pylint: disable=protected-access
        logger.debug('Mogrified: %s', mogrified)

    @staticmethod
    def log_it(conn, message):
        logger.debug(message)

    @staticmethod
    async def _add_log_listener(conn):
        if config.debug:
            logger.debug('Adding Database.log_it log listener')
            conn.add_log_listener(Database.log_it)
        else:
            logger.debug('No need to add Database.log_it')

    @staticmethod
    def _remove_log_listener(conn):
        if config.debug:
            logger.debug('Removing Database.log_it log listener')
            conn.remove_log_listener(Database.log_it)
        else:
            logger.debug('No need to remove Database.log_it')

    @drier
    async def empty(self):
        await self.close()
        con = await self.connect()
        await con.execute('drop owned by current_user cascade')
        await con.close()

    @drier
    async def dropdb(self):
        try:
            await self.close()
            con = await asyncpg.connect(dsn=self.connection_string)
            db_to_drop = con._params.database
            await con.close()

            con = await asyncpg.connect(dsn=self.connection_string, database='')
            await con.execute('drop schema if exists private cascade')
            await con.execute('drop schema if exists public cascade')
            await con.execute('drop database if exists {}'.format(db_to_drop))
            await con.close()
        except asyncpg.exceptions.InvalidCatalogNameError:
            print('Database already dropped')
        except asyncpg.exceptions.ObjectInUseError:
            print("Can't drop the database because it is in use")

    @drier
    async def createdb(self):
        try:
            addrs, params = asyncpg.connect_utils._parse_connect_dsn_and_args(dsn=self.connection_string, host=None, port=None, user=None, password=None, passfile=None, database=None, ssl=None, connect_timeout=None, server_settings=None)
            db_to_create = params.database
            con = await asyncpg.connect(user=params.user, host=addrs[0][0], port=addrs[0][1], password=params.password)
            # role_to_create = params.user
            # result = await con.fetchrow("select count(*) = 0 as not_exists from pg_roles where rolname='{}'".format(role_to_create))
            # if result['not_exists']:
            #     logger.debug('User does %s not exists, create it', role_to_create)
            #     await con.execute("create role musicbot with login password '{}' createdb".format(role_to_create))
            # else:
            #     logger.debug('User %s already exists', role_to_create)

            # as postgresql does not support "create database if not exists", need to check in catalog
            result = await con.fetchrow("select count(*) = 0 as not_exists from pg_catalog.pg_database where datname = '{}'".format(db_to_create))
            if result['not_exists']:
                logger.debug('Database %s does not exists, create it', db_to_create)
                await con.execute('create database {}'.format(db_to_create))
            else:
                logger.debug('Database %s already exists', db_to_create)
            await con.close()
        except ConnectionRefusedError:
            logger.critical('Connection to DB refused, you should check it')
            sys.exit(-1)

    async def connect(self):
        conn = await asyncpg.connect(dsn=self.connection_string, ssl=self._ssl)
        await Database._add_log_listener(conn)
        return conn

    @property
    async def conn(self):
        if self._conn is None:
            self._conn: asyncpg.Connection = await self.connect()
        return self._conn

    @property
    async def pool(self):
        if self._pool is None:
            self._pool: asyncpg.pool.Pool = await asyncpg.create_pool(dsn=self.connection_string, min_size=1, max_size=self.max, setup=Database._add_log_listener, ssl=self._ssl)
        return self._pool

    async def fetch(self, sql, *args):
        if config.debug:
            if self.single:
                await self.mogrify((await self.conn), sql, *args)
                return await (await self.conn).fetch(sql, *args)

            async with (await self.pool).acquire() as connection:
                await self.mogrify(connection, sql, *args)
                results = await connection.fetch(sql, *args)
                Database._remove_log_listener(connection)
                return results
        if self.single:
            return await (await self.conn).fetch(sql, *args)
        return await (await self.pool).fetch(sql, *args)

    async def fetchrow(self, sql, *args):
        if config.debug:
            if self.single:
                await self.mogrify((await self.conn), sql, *args)
                return await (await self.conn).fetchrow(sql, *args)

            async with (await self.pool).acquire() as connection:
                await self.mogrify(connection, sql, *args)
                row = await connection.fetchrow(sql, *args)
                Database._remove_log_listener(connection)
                return row
        if self.single:
            return await (await self.conn).fetchrow(sql, *args)
        return await (await self.pool).fetchrow(sql, *args)

    async def fetchval(self, sql, *args):
        if config.debug:
            if self.single:
                await self.mogrify((await self.conn), sql, *args)
                return await (await self.conn).fetchval(sql, *args)

            async with (await self.pool).acquire() as connection:
                await self.mogrify(connection, sql, *args)
                val = await connection.fetchval(sql, *args)
                Database._remove_log_listener(connection)
                return val
        if self.single:
            return await (await self.conn).fetchval(sql, *args)
        return await (await self.pool).fetchval(sql, *args)

    @drier
    async def executefile(self, filepath):
        schema_path = os.path.join(os.path.dirname(sys.argv[0]), filepath)
        logger.info('loading schema: %s', schema_path)
        with open(schema_path, "r") as s:
            sql = s.read()
            if config.debug:
                if self.single:
                    return await (await self.conn).execute(sql)

                async with (await self.pool).acquire() as connection:
                    async with connection.transaction():
                        result = await connection.execute(sql)
                    Database._remove_log_listener(connection)
                    return result
            if self.single:
                return await (await self.conn).execute(sql)
            await (await self.pool).execute(sql)

    @drier
    async def execute(self, sql, *args):
        if config.debug:
            if self.single:
                await self.mogrify((await self.conn), sql, *args)
                return await (await self.conn).execute(sql, *args)

            async with (await self.pool).acquire() as connection:
                async with connection.transaction():
                    await self.mogrify(connection, sql, *args)
                    result = await connection.execute(sql, *args)
                Database._remove_log_listener(connection)
                return result
        if self.single:
            return await (await self.conn).execute(sql, *args)
        return await (await self.pool).execute(sql, *args)

    @drier
    async def executemany(self, sql, *args, **kwargs):
        if config.debug:
            if self.single:
                return await (await self.conn).executemany(sql, *args, **kwargs)

            async with (await self.pool).acquire() as connection:
                async with connection.transaction():
                    result = await connection.executemany(sql, *args, **kwargs)
                Database._remove_log_listener(connection)
                return result
        if self.single:
            return await (await self.conn).executemany(sql, *args, **kwargs)
        return await (await self.pool).executemany(sql, *args, **kwargs)
