import sys
import os
import click
from logging import debug, info
from .helpers import drier, timeit
from .filter import Filter
import asyncpg
from asyncpg import utils

options = [
    click.option('--host', envvar='MB_DB_HOST', help='DB host', default='localhost'),
    click.option('--port', envvar='MB_DB_PORT', help='DB port', default=5432),
    click.option('--database', envvar='MB_DB', help='DB name', default='musicbot'),
    click.option('--user', envvar='MB_DB_USER', help='DB user', default='postgres'),
    click.option('--password', envvar='MB_DB_PASSWORD', help='DB password', default='musicbot')
]


class DbContext(object):
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

    @drier
    @timeit
    def delete(self, path):
        sql = '''select delete($1)'''
        self.execute(sql, path)

    async def close(self):
        await (await self.pool).close()

    @drier
    @timeit
    async def set_youtube(self, path, youtube):
        sql = '''update musics set youtube=$2 where path=$1'''
        await self.execute(sql, path, youtube)

    @drier
    @timeit
    async def upsert(self, m):
        sql = '''select * from upsert($1::music)'''
        l = m.to_list()
        await self.execute(sql, l)

    @timeit
    async def filter(self, f=None, json=False):
        if f is None:
            f = Filter()
        l = f.to_list()
        if json:
            sql = '''select array_to_json(array_agg(row_to_json(m))) as playlist from do_filter($1::filter) m'''
            return (await self.fetchrow(sql, l))['playlist']
        else:
            sql = '''select * from do_filter($1::filter)'''
            return await self.fetch(sql, l)

    @timeit
    async def playlist(self, f=Filter()):
        sql = '''select * from generate_playlist($1::filter)'''
        l = f.to_list()
        return await self.fetchrow(sql, l)

    @timeit
    async def bests(self, f=Filter()):
        sql = '''select * from generate_bests($1::filter)'''
        l = f.to_list()
        return await self.fetch(sql, l)

    @drier
    @timeit
    async def upsertall(self, musics):
        sql = '''select * from upsert_all($1::music[])'''
        l = [m.to_list() for m in musics]
        await self.execute(sql, l)
        # async with (await self.pool).acquire() as connection:
        #     stmt = await connection.prepare(sql)
        #     print(stmt.get_parameters())
        #     await stmt.fetch(musics)

    def __str__(self):
        return self.connection_string()

    @property
    async def pool(self):
        if self._pool is None:
            self._pool: asyncpg.pool.Pool = await asyncpg.create_pool(**self.settings)
        return self._pool

    @timeit
    async def fetch(self, sql, *args):
        async with (await self.pool).acquire() as connection:
            mogrified = await utils._mogrify(connection, sql, args)
            info('mogrified: {}'.format(mogrified))
            return await connection.fetch(sql, *args)

    @timeit
    async def fetchrow(self, sql, *args):
        async with (await self.pool).acquire() as connection:
            mogrified = await utils._mogrify(connection, sql, args)
            info('mogrified: {}'.format(mogrified))
            return await connection.fetchrow(sql, *args)

    @drier
    @timeit
    async def executefile(self, filepath):
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
                mogrified = await utils._mogrify(connection, sql, args)
                info('mogrified: {}'.format(mogrified))
                await connection.execute(sql, *args)

    @drier
    @timeit
    async def executemany(self, sql, *args, **kwargs):
        debug(sql)
        async with (await self.pool).acquire() as connection:
            async with connection.transaction():
                await connection.executemany(sql, *args, **kwargs)

    @drier
    @timeit
    async def create(self):
        debug('db create')
        sql = 'create schema if not exists {}'.format(self.schema)
        await self.execute(sql)
        await self.executefile('schema/tables.sql')
        await self.executefile('schema/functions.sql')

    @drier
    @timeit
    async def drop(self):
        debug('db drop')
        sql = 'drop schema if exists {} cascade'.format(self.schema)
        await self.execute(sql)

    @drier
    @timeit
    async def clear(self):
        debug('clear')
        await self.drop()
        await self.create()

    @timeit
    async def folders(self):
        sql = '''select name from folders'''
        return await self.fetch(sql)

    @timeit
    async def keywords(self, mf=Filter()):
        # sql = """select coalesce(array_agg(distinct keywords), array[]::text[]) as keywords from (select unnest(array_cat_agg(keywords)) as keywords from do_filter($1::filter)) k"""
        # return (await self.fetchrow(sql, mf.to_list()))['keywords']
        sql = """select distinct keyword as name from (select unnest(array_cat_agg(keywords)) as keyword from do_filter($1::filter)) k"""
        return [f['name'] for f in (await self.fetch(sql, mf.to_list()))]

    @timeit
    async def artists(self, mf=Filter()):
        # sql = """select coalesce(array_agg(distinct artist), array[]::text[]) as artists from do_filter($1::filter)"""
        # return (await self.fetchrow(sql, mf.to_list()))['artists']
        sql = """select distinct artist as name from do_filter($1::filter)"""
        return [f['name'] for f in (await self.fetch(sql, mf.to_list()))]

    @timeit
    async def titles(self, mf=Filter()):
        # sql = """select coalesce(array_agg(distinct title), array[]::text[]) as titles from do_filter($1::filter)"""
        # return (await self.fetchrow(sql, mf.to_list()))['titles']
        sql = """select distinct title as name from do_filter($1::filter)"""
        return [f['name'] for f in (await self.fetch(sql, mf.to_list()))]

    @timeit
    async def albums(self, mf=Filter()):
        # sql = """select coalesce(array_agg(distinct album), array[]::text[]) as albums from do_filter($1::filter)"""
        # return (await self.fetchrow(sql, mf.to_list()))['albums']
        sql = """select distinct album as name from do_filter($1::filter)"""
        return [f['name'] for f in (await self.fetch(sql, mf.to_list()))]

    @timeit
    async def genres(self, mf=Filter()):
        # sql = """select coalesce(array_agg(distinct genre), array[]::text[]) as genres from do_filter($1::filter)"""
        # return (await self.fetchrow(sql, mf.to_list()))['genres']
        sql = """select distinct genre as name from do_filter($1::filter)"""
        return [f['name'] for f in (await self.fetch(sql, mf.to_list()))]

    @timeit
    async def form(self, mf=Filter()):
        sql = '''select * from generate_form($1::filter)'''
        return await self.fetchrow(sql, mf.to_list())

    @timeit
    async def stats(self, mf=Filter()):
        sql = '''select * from do_stats($1::filter)'''
        return await self.fetchrow(sql, mf.to_list())
