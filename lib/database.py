# -*- coding: utf-8 -*-
import click
import os
from asyncpg import utils, connect
from logging import debug, info
from .helpers import drier, timeit

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 5432
DEFAULT_DATABASE = 'musicbot_prod'
DEFAULT_USER = 'postgres'
DEFAULT_PASSWORD = 'musicbot'

options = [
    click.option('--db-host', envvar='MB_DB_HOST', help='DB host', default=DEFAULT_HOST),
    click.option('--db-port', envvar='MB_DB_PORT', help='DB port', default=DEFAULT_PORT),
    click.option('--db-database', envvar='MB_DATABASE', help='DB name', default=DEFAULT_DATABASE),
    click.option('--db-user', envvar='MB_DB_USER', help='DB user', default=DEFAULT_USER),
    click.option('--db-password', envvar='MB_DB_PASSWORD', help='DB password', default=DEFAULT_PASSWORD)
]


class Database(object):
    def __init__(self, max_conn=100, **kwargs):
        self.set(**kwargs)
        self.max_conn = max_conn

    def set(self, db_host=None, db_port=None, db_database=None, db_user=None, db_password=None, **kwargs):
        self.host = db_host if db_host is not None else os.getenv('MB_DB_HOST', DEFAULT_HOST)
        self.port = db_port if db_port is not None else os.getenv('MB_DB_PORT', DEFAULT_PORT)
        self.database = db_database if db_database is not None else os.getenv('MB_DATABASE', DEFAULT_DATABASE)
        self.user = db_user if db_user is not None else os.getenv('MB_DB_USER', DEFAULT_USER)
        self.password = db_password if db_password is not None else os.getenv('MB_DB_PASSWORD', DEFAULT_PASSWORD)
        self._pool = None
        info('Database: {}'.format(self.connection_string()))

    def connection_string(self):
        return 'postgresql://{}:{}@{}:{}/{}'.format(self.user, self.password, self.host, self.port, self.database)

    async def close(self):
        await (await self.pool).close()

    def __str__(self):
        return self.connection_string()

    async def mogrify(self, connection, sql, *args):
        mogrified = await utils._mogrify(connection, sql, args)
        info('mogrified: {}'.format(mogrified))

    @drier
    async def dropdb(self):
        con = await connect(user=self.user, host=self.host, password=self.password, port=self.port)
        await con.execute('drop database if exists {}'.format(self.database))
        await con.close()

    @drier
    async def createdb(self):
        con = await connect(user=self.user, host=self.host, password=self.password, port=self.port)
        await con.execute('create database {}'.format(self.database))
        await con.close()

    @property
    async def pool(self):
        if self._pool is None:
            import asyncpg
            self._pool: asyncpg.pool.Pool = await asyncpg.create_pool(max_size=self.max_conn, user=self.user, host=self.host, password=self.password, port=self.port, database=self.database)
        return self._pool

    @timeit
    async def fetch(self, sql, *args):
        async with (await self.pool).acquire() as connection:
            await self.mogrify(connection, sql, *args)
            return await connection.fetch(sql, *args)

    @timeit
    async def fetchrow(self, sql, *args):
        async with (await self.pool).acquire() as connection:
            await self.mogrify(connection, sql, *args)
            return await connection.fetchrow(sql, *args)

    @drier
    @timeit
    async def executefile(self, filepath):
        import sys
        import os
        schema_path = os.path.join(os.path.dirname(sys.argv[0]), filepath)
        info('loading schema: {}'.format(schema_path))
        with open(schema_path, "r") as s:
            sql = s.read()
            async with (await self.pool).acquire() as connection:
                async with connection.transaction():
                    await connection.execute(sql)

    @drier
    @timeit
    async def execute(self, sql, *args, **kwargs):
        async with (await self.pool).acquire() as connection:
            async with connection.transaction():
                await self.mogrify(connection, sql, *args)
                await connection.execute(sql, *args)

    @drier
    @timeit
    async def executemany(self, sql, *args, **kwargs):
        debug(sql)
        async with (await self.pool).acquire() as connection:
            async with connection.transaction():
                await connection.executemany(sql, *args, **kwargs)
