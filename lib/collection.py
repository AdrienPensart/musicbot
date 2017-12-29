# -*- coding: utf-8 -*-
from .filter import Filter
from .database import Database
from .helpers import drier, timeit
from logging import debug


class Collection(Database):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @drier
    @timeit
    async def create(self):
        debug('db create')
        sql = 'create schema if not exists {}'.format(self.schema)
        await self.execute(sql)
        await self.executefile('schema/tables.sql')
        await self.executefile('schema/functions.sql')
        await self.executefile('schema/data.sql')

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
        sql = """select distinct keyword as name from (select unnest(array_cat_agg(keywords)) as keyword from do_filter($1::filters)) k order by name"""
        return [f['name'] for f in (await self.fetch(sql, mf.to_list()))]

    @timeit
    async def artists(self, mf=Filter()):
        sql = """select distinct artist as name from do_filter($1::filters) order by name"""
        return [f['name'] for f in (await self.fetch(sql, mf.to_list()))]

    @timeit
    async def titles(self, mf=Filter()):
        sql = """select distinct title as name from do_filter($1::filters) order by name"""
        return [f['name'] for f in (await self.fetch(sql, mf.to_list()))]

    @timeit
    async def albums(self, mf=Filter(), youtube=''):
        sql = """select album as name, artist, a.youtube as youtube, album_id as id, sum(duration) as duration from do_filter($1::filters) m inner join albums a on a.id=album_id where $2::text is null or $2::text = a.youtube group by m.album_id, m.artist_id, artist, album, a.youtube order by album"""
        return await self.fetch(sql, mf.to_list(), youtube)

    @timeit
    async def albums_name(self, mf=Filter()):
        return [f['name'] for f in (await self.albums(mf))]

    @timeit
    async def genres(self, mf=Filter()):
        sql = """select distinct genre as name from do_filter($1::filters) order by name"""
        return [f['name'] for f in (await self.fetch(sql, mf.to_list()))]

    @timeit
    async def form(self, mf=Filter()):
        sql = '''select * from generate_form($1::filters)'''
        return await self.fetchrow(sql, mf.to_list())

    @timeit
    async def stats(self, mf=Filter()):
        sql = '''select * from do_stats($1::filters)'''
        return await self.fetchrow(sql, mf.to_list())

    @timeit
    async def filters(self):
        sql = '''select * from filters'''
        return await self.fetch(sql)

    @timeit
    async def get_filter(self, name):
        sql = '''select * from filters where name=$1'''
        return await self.fetchrow(sql, name)

    @drier
    @timeit
    async def set_music_youtube(self, path, youtube):
        sql = '''update musics set youtube=$2 where path=$1'''
        await self.execute(sql, path, youtube)

    @drier
    @timeit
    async def set_album_youtube(self, id, youtube):
        sql = '''update albums set youtube=$2 where id=$1'''
        await self.execute(sql, id, youtube)

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
            sql = '''select array_to_json(array_agg(row_to_json(m))) as playlist from do_filter($1::filters) m'''
            return (await self.fetchrow(sql, l))['playlist']
        else:
            sql = '''select * from do_filter($1::filters)'''
            return await self.fetch(sql, l)

    @timeit
    async def playlist(self, f=Filter()):
        sql = '''select * from generate_playlist($1::filters)'''
        l = f.to_list()
        return await self.fetchrow(sql, l)

    @timeit
    async def bests(self, f=Filter()):
        sql = '''select * from generate_bests($1::filters)'''
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
    async def delete(self, path):
        sql = '''select delete($1)'''
        await self.execute(sql, path)
