from logging import debug, info
from .helpers import drier, timeit
from .filter import Filter
import asyncpg
import sys
import os


# class DbContext(metaclass=Synchronizer):
class DbContext(object):
    settings = {
        'host': 'localhost',
        'port': 5432,
        'database': 'musicbot',
        'user': 'postgres',
        'password': 'musicbot', }
    schema = 'public'
    insert_log = '''insert into musics_log (artist, album, genre, folder, youtube, number, rating, duration, size, title, path, keywords) values ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)'''

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

    @drier
    @timeit
    async def upsert(self, m):
        sql = '''select * from upsert($1::music)'''
        l = m.to_list()
        await self.execute(sql, l)

    async def filter(self, f=Filter()):
        sql = '''select * from do_filter($1::filter)'''
        l = f.to_list()
        return await self.fetch(sql, l)

    async def playlist(self, f=Filter()):
        sql = '''select * from generate_playlist($1::filter)'''
        l = f.to_list()
        return await self.fetchrow(sql, l)

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

    @drier
    @timeit
    async def append(self, m):
        await self.execute(self.insert_log, m.artist, m.album, m.genre, m.folder, m.youtube, m.number, m.rating, m.duration, m.size, m.title, m.path, m.keywords)

    @drier
    @timeit
    async def appendall(self, musics):
        for m in musics:
            await self.execute(self.insert_log, m.artist, m.album, m.genre, m.folder, m.youtube, m.number, m.rating, m.duration, m.size, m.title, m.path, m.keywords)

    @drier
    @timeit
    async def appendmany(self, musics):
        async with (await self.pool).acquire() as connection:
            await connection.executemany(self.insert_log, musics)
        # await self.executemany(sql, musics)

    def __str__(self):
        return self.connection_string()

    @property
    async def pool(self):
        if self._pool is None:
            self._pool: asyncpg.pool.Pool = await asyncpg.create_pool(**self.settings)
        return self._pool

    @timeit
    async def fetch(self, *args, **kwargs):
        info('fetching: {}'.format(*args))
        return (await (await self.pool).fetch(*args, **kwargs))

    @timeit
    async def fetchrow(self, *args, **kwargs):
        info('fetching row: {}'.format(*args))
        return (await (await self.pool).fetchrow(*args, **kwargs))

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
        debug(sql)
        async with (await self.pool).acquire() as connection:
            async with connection.transaction():
                await connection.execute(sql, *args, **kwargs)

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
        await self.executefile('lib/musicbot.sql')

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
    async def keywords(self, mf=Filter(), fast=False):
        if fast:
            sql = """select distinct name from tags"""
            return await self.fetch(sql)
        else:
            if mf is None:
                sql = """select coalesce(array_agg(distinct name), array[]::text[]) as keywords from tags"""
            else:
                sql = """select coalesce(array_agg(distinct keywords), array[]::text[]) as keywords from (select unnest(array_cat_agg(keywords)) as keywords from do_filter($1::filter)) k"""
        return (await self.fetchrow(sql, mf.to_list()))['keywords']

    @timeit
    async def artists(self, mf=Filter(), fast=False):
        if fast:
            sql = """select distinct name from artists"""
            return await self.fetch(sql)
        else:
            if mf is None:
                sql = """select coalesce(array_agg(distinct name), array[]::text[]) as artists from artists"""
            else:
                sql = """select coalesce(array_agg(distinct artist), array[]::text[]) as artists from do_filter($1::filter)"""
        return (await self.fetchrow(sql, mf.to_list()))['artists']

    @timeit
    async def titles(self, mf=Filter(), fast=False):
        if fast:
            sql = """select distinct title as name from musics"""
            return await self.fetch(sql)
        else:
            if mf is None:
                sql = """select coalesce(array_agg(distinct title), array[]::text[]) as titles from musics"""
            else:
                sql = """select coalesce(array_agg(distinct title), array[]::text[]) as titles from do_filter($1::filter)"""
        return (await self.fetchrow(sql, mf.to_list()))['titles']

    @timeit
    async def albums(self, mf=Filter(), fast=False):
        if fast:
            sql = """select distinct name from albums"""
            return await self.fetch(sql)
        else:
            if mf is None:
                sql = """select coalesce(array_agg(distinct name), array[]::text[]) as albums from albums"""
            else:
                sql = """select coalesce(array_agg(distinct album), array[]::text[]) as albums from do_filter($1::filter)"""
        return (await self.fetchrow(sql, mf.to_list()))['albums']

    @timeit
    async def genres(self, mf=Filter(), fast=False):
        if fast:
            sql = """select distinct name from genres"""
            return self.fetch(sql)
        else:
            if mf is None:
                sql = """select coalesce(array_agg(distinct name), array[]::text[]) as genres from genres"""
            else:
                sql = """select coalesce(array_agg(distinct genre), array[]::text[]) as genres from do_filter($1::filter)"""
        return (await self.fetchrow(sql, mf.to_list()))['genres']

    @timeit
    async def form(self, mf=Filter()):
        sql = '''select * from generate_form($1::filter)'''
        return await self.fetchrow(sql, mf.to_list())

    @timeit
    async def stats(self, mf=Filter()):
        sql = 'select * from do_stats($1::filter)'
        return await self.fetchrow(sql, mf.to_list())
