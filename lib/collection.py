import os
import logging
from .mfilter import Filter
from .database import Database
from .helpers import drier, timeit

logger = logging.getLogger(__name__)


class Collection(Database):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def errors(self, mf=None):
        return ['not implemented for {}'.format(mf)]

    async def create(self, schema_dir):
        await self.createdb()
        for sqlfile in ['tables.sql', 'views.sql', 'functions.sql', 'data.sql', 'triggers.sql']:
            await self.executefile(os.path.join(schema_dir, sqlfile))

    async def clear(self, schema_dir):
        await self.dropdb()
        await self.create(schema_dir)

    async def drop(self):
        await self.dropdb()

    async def refresh(self):
        sql = 'select refresh_views()'
        await self.execute(sql)

    async def folders(self, json=False):
        if json:
            sql = '''select array_to_json(array_agg(row_to_json(f))) as result from folders f'''
            return (await self.fetchrow(sql))['result']
        sql = '''select name from folders order by name'''
        return await self.fetch(sql)

    async def folders_name(self):
        return [f['name'] for f in (await self.folders())]

    async def new_folder(self, name):
        sql = '''insert into folders as f(name, created_at, updated_at) values ($1, now(), now())'''
        return await self.execute(sql, name)

    async def keywords(self, mf=None, json=False):
        if mf is None:
            mf = Filter()
        tl = mf.to_list()
        if json:
            sql = '''select array_to_json(array_agg(row_to_json(k))) as json from (select distinct keyword as name from (select unnest(array_cat_agg(keywords)) as keyword from do_filter($1::filters)) k order by name) k'''
            return (await self.fetchrow(sql, tl))['json']
        sql = """select distinct keyword as name from (select unnest(array_cat_agg(keywords)) as keyword from do_filter($1::filters)) k order by name"""
        return await self.fetch(sql, tl)

    async def keywords_name(self, mf=None):
        return [f['name'] for f in (await self.keywords(mf))]

    async def artists(self, mf=None, json=False):
        if mf is None:
            mf = Filter()
        tl = mf.to_list()
        if json:
            sql = '''select array_to_json(array_agg(row_to_json(a))) as json from (select distinct artist as name from do_filter($1::filters) m order by name) a'''
            return (await self.fetchrow(sql, tl))['json']
        sql = """select distinct artist as name from do_filter($1::filters) order by name"""
        return await self.fetch(sql, tl)

    async def artists_name(self, mf=None):
        return [f['name'] for f in (await self.artists(mf))]

    async def titles(self, mf=None, json=False):
        if mf is None:
            mf = Filter()
        if json:
            sql = '''select array_to_json(array_agg(row_to_json(a))) as json from (select distinct title as name from do_filter($1::filters) order by name) a'''
        sql = """select distinct title as name from do_filter($1::filters) order by name"""
        return await self.fetch(sql, mf.to_list())

    async def titles_name(self, mf=None):
        return [f['name'] for f in (await self.titles(mf))]

    async def albums(self, mf=None, youtube=None, json=False):
        if mf is None:
            mf = Filter()
        tl = mf.to_list()
        if json:
            sql = '''select array_to_json(array_agg(row_to_json(a))) as json from (select album as name, artist, a.youtube as youtube, sum(duration) as duration from do_filter($1::filters) m inner join albums a on a.name=album where $2::text is null or $2::text = a.youtube group by album, artist, a.youtube order by album) a'''
            return (await self.fetchrow(sql, tl, youtube))['json']
        sql = """select album as name, artist, a.youtube as youtube, sum(duration) as duration from do_filter($1::filters) m inner join albums a on a.name=album where $2::text is null or $2::text = a.youtube group by album, artist, a.youtube order by album"""
        return await self.fetch(sql, tl, youtube)

    async def albums_name(self, mf=None):
        return [f['name'] for f in (await self.albums(mf))]

    async def genres(self, mf=None, json=False):
        if mf is None:
            mf = Filter()
        tl = mf.to_list()
        if json:
            sql = '''select array_to_json(array_agg(row_to_json(g))) as json from (select distinct genre as name from do_filter($1::filters) m order by name) g'''
            return (await self.fetchrow(sql, tl))['json']
        sql = """select distinct genre as name from do_filter($1::filters) order by name"""
        return await self.fetch(sql, tl)

    async def genres_name(self, mf=None):
        return [f['name'] for f in (await self.genres(mf))]

    # async def form(self, mf=None):
    #     if mf is None:
    #         mf = Filter()
    #     sql = '''select * from generate_form($1::filters)'''
    #     return await self.fetchrow(sql, mf.to_list())

    async def stats(self, mf=None, json=False):
        if mf is None:
            mf = Filter()
        tl = mf.to_list()
        if json:
            sql = '''select row_to_json(s) as json from do_stats($1::filters) s'''
            return (await self.fetchrow(sql, tl))['json']
        sql = '''select * from do_stats($1::filters) s'''
        return await self.fetchrow(sql, tl)

    async def filters(self, json=False):
        if json:
            sql = '''select array_to_json(array_agg(row_to_json(f))) as json from filters f'''
            return (await self.fetchrow(sql))['json']
        sql = '''select * from filters'''
        return await self.fetch(sql)

    async def get_filter(self, name):
        sql = '''select * from filters where name=$1'''
        return await self.fetchrow(sql, name)

    @drier
    async def set_music_youtube(self, path, youtube):
        sql = '''update musics set youtube=$2 where path=$1'''
        await self.execute(sql, path, youtube)

    @drier
    async def set_album_youtube(self, name, youtube):
        sql = '''update albums set youtube=$2 where name=$1'''
        await self.execute(sql, name, youtube)

    @drier
    async def upsert(self, m):
        sql = '''select * from upsert($1::music)'''
        tl = m.to_list()
        await self.execute(sql, tl)

    @timeit
    async def musics(self, f=None, json=False):
        if f is None:
            f = Filter()
        tl = f.to_list()
        if json:
            sql = '''select array_to_json(array_agg(row_to_json(m))) as playlist from do_filter($1::filters) m'''
            return (await self.fetchrow(sql, tl))['playlist']
        sql = '''select * from do_filter($1::filters)'''
        return await self.fetch(sql, tl)

    async def music(self, music_id, json=False):
        if json:
            sql = '''select array_to_json(array_agg(row_to_json(m))) as music from mmusics m where m.id=$1 limit 1'''
            return (await self.fetchrow(sql, music_id))['music']
        sql = '''select * from mmusics m where m.id=$1 limit 1'''
        return await self.fetchrow(sql, music_id)

    @drier
    # async def update_music(self, id, title, artist, album, genre, youtube, track, keywords, rating):
    async def update_music(self, *args):
        sql = '''update mmusics set title = $2, artist= $3, album = $4, genre = $5, youtube = $6, track = $7, keywords = $8, rating = $9 where m.id=$1 limit 1'''
        # return await self.execute(sql, id, title, artist, album, genre, youtube, track, keywords, rating)
        return await self.execute(sql, *args)

    async def playlist(self, f=None):
        if f is None:
            f = Filter()
        sql = '''select * from generate_playlist($1::filters)'''
        tl = f.to_list()
        return await self.fetchrow(sql, tl)

    async def bests(self, f=None):
        if f is None:
            f = Filter()
        sql = '''select * from generate_bests($1::filters)'''
        tl = f.to_list()
        return await self.fetch(sql, tl)

    @drier
    async def delete(self, path):
        sql = '''select delete($1)'''
        await self.execute(sql, path)
