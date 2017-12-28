# -*- coding: utf-8 -*-
import click
from logging import debug, info
from .helpers import drier, timeit

options = [
    click.option('--host', envvar='MB_DB_HOST', help='DB host', default='localhost'),
    click.option('--port', envvar='MB_DB_PORT', help='DB port', default=5432),
    click.option('--database', envvar='MB_DB', help='DB name', default='musicbot'),
    click.option('--user', envvar='MB_DB_USER', help='DB user', default='postgres'),
    click.option('--password', envvar='MB_DB_PASSWORD', help='DB password', default='musicbot')
]


class Database(object):
    settings = {
        'host': 'localhost',
        'port': 5432,
        'database': 'musicbot',
        'user': 'postgres',
        'password': 'musicbot', }
    schema = 'public'

    def __init__(self, **kwargs):
        for s in self.settings.keys():
            if s in kwargs:
                self.settings[s] = kwargs[s]
        self._pool = None
        info(self.connection_string())

    def connection_string(self):
        return 'postgresql://{}:{}@{}:{}/{}'.format(self.settings['user'], self.settings['password'], self.settings['host'], self.settings['port'], self.settings['database'])

    async def close(self):
        await (await self.pool).close()

    def __str__(self):
        return self.connection_string()

    async def mogrify(self, connection, sql, *args):
        from asyncpg import utils
        mogrified = await utils._mogrify(connection, sql, args)
        info('mogrified: {}'.format(mogrified))

    @property
    async def pool(self):
        if self._pool is None:
            import asyncpg
            self._pool: asyncpg.pool.Pool = await asyncpg.create_pool(**self.settings)
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
