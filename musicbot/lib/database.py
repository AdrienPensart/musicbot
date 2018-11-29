import os
import sys
import logging
import ssl
import click
import asyncpg

from . import lib
from .helpers import drier, timeit
from .config import config
from .mfilter import Filter

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
    click.option('--db-single', envvar=MB_DB_SINGLE, help='DB will use only one connection', default=DEFAULT_DB_SINGLE, is_flag=True, show_default=True),
    click.option('--db-cert', envvar=MB_DB_CERT, help='DB SSL certificate', default=DEFAULT_DB_CERT, show_default=True)
]


class Database:
    auth = None

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

    @classmethod
    async def make(cls, skip_creation=False, **kwargs):
        self = Database(**kwargs)
        if not skip_creation:
            await self.create()
        return self

    async def errors(self, mf=None):
        return ['not implemented for {}'.format(mf)]

    async def create(self):
        await self.createdb()
        schema_dir = os.path.join(os.path.dirname(__file__), 'schema')
        for sqlfile in ['schemas.sql', 'extensions.sql', 'users.sql', 'raw_music.sql', 'filter.sql', 'stat.sql']:
            await self.executefile(os.path.join(schema_dir, sqlfile))

    async def clear(self):
        await self.dropdb()
        await self.create()

    async def drop(self):
        logger.info("Dropping DB")
        await self.dropdb()

    async def register_user(self, first_name, last_name, email, password):
        sql = '''select * from musicbot_public.register_user($1, $2, $3, $4)'''
        return await self.fetchrow(sql, first_name, last_name, email, password)

    async def remove_user(self, email):
        sql = '''select * from musicbot_public.remove_user($1)'''
        return await self.fetchrow(sql, email)

    async def authenticate_user(self, email, password):
        sql = '''select * from musicbot_public.authenticate($1, $2)'''
        Database.auth = await self.fetchrow(sql, email, password)
        return Database.auth

    async def new_token(self, email, password, secret):
        sql = '''select * from musicbot_public.new_token($1, $2, $3)'''
        return await self.fetchrow(sql, email, password, secret)

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
            sql = '''select array_to_json(array_agg(row_to_json(k))) as json from (select distinct keyword as name from (select unnest(array_cat_agg(keywords)) as keyword from do_filter($1::musicbot_public.filter)) k order by name) k'''
            return (await self.fetchrow(sql, tl))['json']
        sql = """select distinct keyword as name from (select unnest(array_cat_agg(keywords)) as keyword from do_filter($1::musicbot_public.filter)) k order by name"""
        return await self.fetch(sql, tl)

    async def keywords_name(self, mf=None):
        return [f['name'] for f in (await self.keywords(mf))]

    async def artists(self, mf=None, json=False):
        if mf is None:
            mf = Filter()
        tl = mf.to_list()
        if json:
            sql = '''select array_to_json(array_agg(row_to_json(a))) as json from (select distinct artist as name from do_filter($1::musicbot_public.filter) m order by name) a'''
            return (await self.fetchrow(sql, tl))['json']
        sql = """select distinct artist as name from do_filter($1::musicbot_public.filter) order by name"""
        return await self.fetch(sql, tl)

    async def artists_name(self, mf=None):
        return [f['name'] for f in (await self.artists(mf))]

    async def titles(self, mf=None, json=False):
        if mf is None:
            mf = Filter()
        if json:
            sql = '''select array_to_json(array_agg(row_to_json(a))) as json from (select distinct title as name from do_filter($1::musicbot_public.filter) order by name) a'''
        sql = """select distinct title as name from do_filter($1::musicbot_public.filter) order by name"""
        return await self.fetch(sql, mf.to_list())

    async def titles_name(self, mf=None):
        return [f['name'] for f in (await self.titles(mf))]

    async def albums(self, mf=None, youtube=None, json=False):
        if mf is None:
            mf = Filter()
        tl = mf.to_list()
        if json:
            sql = '''select array_to_json(array_agg(row_to_json(a))) as json from (select album as name, artist, a.youtube as youtube, sum(duration) as duration from do_filter($1::musicbot_public.filter) m inner join albums a on a.name=album where $2::text is null or $2::text = a.youtube group by album, artist, a.youtube order by album) a'''
            return (await self.fetchrow(sql, tl, youtube))['json']
        sql = """select album as name, artist, a.youtube as youtube, sum(duration) as duration from do_filter($1::musicbot_public.filter) m inner join albums a on a.name=album where $2::text is null or $2::text = a.youtube group by album, artist, a.youtube order by album"""
        return await self.fetch(sql, tl, youtube)

    async def albums_name(self, mf=None):
        return [f['name'] for f in (await self.albums(mf))]

    async def genres(self, mf=None, json=False):
        if mf is None:
            mf = Filter()
        tl = mf.to_list()
        if json:
            sql = '''select array_to_json(array_agg(row_to_json(g))) as json from (select distinct genre as name from do_filter($1::musicbot_public.filter) m order by name) g'''
            return (await self.fetchrow(sql, tl))['json']
        sql = """select distinct genre as name from do_filter($1::musicbot_public.filter) order by name"""
        return await self.fetch(sql, tl)

    async def genres_name(self, mf=None):
        return [f['name'] for f in (await self.genres(mf))]

    # async def form(self, mf=None):
    #     if mf is None:
    #         mf = Filter()
    #     sql = '''select * from generate_form($1::musicbot_public.filter)'''
    #     return await self.fetchrow(sql, mf.to_list())

    async def stats(self, mf=None, json=False):
        if mf is None:
            mf = Filter()
        tl = mf.to_list()
        if json:
            sql = '''select row_to_json(s) as json from do_stats($1::musicbot_public.filter) s'''
            return (await self.fetchrow(sql, tl))['json']
        sql = '''select * from do_stats($1::musicbot_public.filter) s'''
        return await self.fetchrow(sql, tl)

    async def filters(self, json=False):
        if json:
            sql = '''select array_to_json(array_agg(row_to_json(f))) as json from musicbot_public.filter f'''
            return (await self.fetchrow(sql))['json']
        sql = '''select * from musicbot_public.filter'''
        return await self.fetch(sql)

    async def get_filter(self, name):
        sql = '''select * from musicbot_public.filter where name=$1'''
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
        sql = '''select * from musicbot_public.upsert($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)'''
        tl = m.to_list()
        await self.execute(sql, *tl)

    @timeit
    async def musics(self, f=None, json=False):
        if f is None:
            f = Filter()
        tl = f.to_list()
        if json:
            sql = '''select array_to_json(array_agg(row_to_json(m))) as playlist from do_filter($1::musicbot_public.filter) m'''
            return (await self.fetchrow(sql, tl))['playlist']
        sql = '''select * from do_filter($1::musicbot_public.filter)'''
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
        sql = '''select * from generate_playlist($1::musicbot_public.filter)'''
        tl = f.to_list()
        return await self.fetchrow(sql, tl)

    async def bests(self, f=None):
        if f is None:
            f = Filter()
        sql = '''select * from generate_bests($1::musicbot_public.filter)'''
        tl = f.to_list()
        return await self.fetch(sql, tl)

    @drier
    async def delete(self, path):
        sql = '''select delete($1)'''
        await self.execute(sql, path)

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
    def _log_it(conn, message):
        logger.debug(message)

    @staticmethod
    async def _setup(conn):
        if Database.auth is not None:
            await conn.execute('''select set_config('jwt.claims.role', $1, false)''', Database.auth['role'])
            await conn.execute('''select set_config('jwt.claims.user_id', $1, false)''', str(Database.auth['user_id']))
            logger.debug('%s auth used to setup connection', Database.auth)
        Database._add_log_listener(conn)

    @staticmethod
    def _add_log_listener(conn):
        if config.debug:
            logger.debug('Adding Database._log_it log listener')
            conn.add_log_listener(Database._log_it)
        else:
            logger.debug('No need to add Database._log_it')

    @staticmethod
    def _remove_log_listener(conn):
        if config.debug:
            logger.debug('Removing Database._log_it log listener')
            conn.remove_log_listener(Database._log_it)
        else:
            logger.debug('No need to remove Database._log_it')

    @drier
    async def empty(self):
        await self.close()
        con = await self.connect()
        await con.execute('drop owned by current_user cascade')
        await con.close()

    @drier
    async def createdb(self):
        try:
            addrs, params = asyncpg.connect_utils._parse_connect_dsn_and_args(dsn=self.connection_string,
                                                                              host=None,
                                                                              port=None,
                                                                              user=None,
                                                                              password=None,
                                                                              passfile=None,
                                                                              database=None,
                                                                              ssl=None,
                                                                              connect_timeout=None,
                                                                              server_settings=None)
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

    @drier
    async def dropdb(self):
        try:
            await self.close()
            con = await asyncpg.connect(dsn=self.connection_string)
            db_to_drop = con._params.database
            await con.close()

            con = await asyncpg.connect(dsn=self.connection_string, database='')
            await con.execute('''
                select pg_terminate_backend(pg_stat_activity.pid)
                from pg_stat_activity
                where pg_stat_activity.datname = '{}' and pid <> pg_backend_pid()'''.format(db_to_drop))
            await con.execute('drop schema if exists musicbot_private cascade')
            await con.execute('drop schema if exists musicbot_public cascade')
            await con.execute('drop database if exists {}'.format(db_to_drop))
            await con.close()
        except asyncpg.exceptions.InvalidCatalogNameError:
            print('Database already dropped')
        except asyncpg.exceptions.ObjectInUseError:
            print("Can't drop the database because it is in use")

    async def connect(self):
        conn = await asyncpg.connect(dsn=self.connection_string, ssl=self._ssl)
        Database._add_log_listener(conn)
        return conn

    @property
    async def conn(self):
        if self._conn is None:
            self._conn: asyncpg.Connection = await self.connect()
        return self._conn

    @property
    async def pool(self):
        if self._pool is None:
            self._pool: asyncpg.pool.Pool = await asyncpg.create_pool(dsn=self.connection_string,
                                                                      min_size=1,
                                                                      max_size=self.max,
                                                                      setup=Database._setup,
                                                                      ssl=self._ssl)
        return self._pool

    async def fetch(self, sql, *args):
        if config.debug:
            if self.single:
                await self.mogrify((await self.conn), sql, *args)
                c = await self.conn
                return await c.fetch(sql, *args)

            async with (await self.pool).acquire() as connection:
                await self.mogrify(connection, sql, *args)
                results = await connection.fetch(sql, *args)
                Database._remove_log_listener(connection)
                return results
        if self.single:
            c = await self.conn
            return await c.fetch(sql, *args)
        p = await self.pool
        return await p.fetch(sql, *args)

    async def fetchrow(self, sql, *args):
        if config.debug:
            if self.single:
                c = await self.conn
                await self.mogrify(c, sql, *args)
                return await c.fetchrow(sql, *args)

            async with (await self.pool).acquire() as connection:
                await self.mogrify(connection, sql, *args)
                row = await connection.fetchrow(sql, *args)
                Database._remove_log_listener(connection)
                return row
        if self.single:
            c = await self.conn
            return await c.fetchrow(sql, *args)
        p = await self.pool
        return await p.fetchrow(sql, *args)

    async def fetchval(self, sql, *args):
        if config.debug:
            if self.single:
                c = await self.conn
                await self.mogrify(c, sql, *args)
                return await c.fetchval(sql, *args)

            async with (await self.pool).acquire() as connection:
                await self.mogrify(connection, sql, *args)
                val = await connection.fetchval(sql, *args)
                Database._remove_log_listener(connection)
                return val
        if self.single:
            c = await self.conn
            return await c.fetchval(sql, *args)
        p = await self.pool
        return await p.fetchval(sql, *args)

    @drier
    async def executefile(self, filepath):
        schema_path = os.path.join(os.path.dirname(sys.argv[0]), filepath)
        logger.info('loading schema: %s', schema_path)
        with open(schema_path, "r") as s:
            sql = s.read()
            if config.debug:
                if self.single:
                    c = await self.conn
                    return await c.execute(sql)

                async with (await self.pool).acquire() as connection:
                    async with connection.transaction():
                        result = await connection.execute(sql)
                    Database._remove_log_listener(connection)
                    return result
            if self.single:
                c = await self.conn
                return await c.execute(sql)
            p = await self.pool
            await p.execute(sql)

    @drier
    async def execute(self, sql, *args):
        if config.debug:
            if self.single:
                c = await self.conn
                await self.mogrify(c, sql, *args)
                return await c.execute(sql, *args)

            async with (await self.pool).acquire() as connection:
                async with connection.transaction():
                    await self.mogrify(connection, sql, *args)
                    result = await connection.execute(sql, *args)
                Database._remove_log_listener(connection)
                return result
        if self.single:
            c = await self.conn
            return await c.execute(sql, *args)
        p = await self.pool
        return await p.execute(sql, *args)

    @drier
    async def executemany(self, sql, *args, **kwargs):
        if config.debug:
            if self.single:
                c = await self.conn
                return await c.executemany(sql, *args, **kwargs)

            async with (await self.pool).acquire() as connection:
                async with connection.transaction():
                    result = await connection.executemany(sql, *args, **kwargs)
                Database._remove_log_listener(connection)
                return result
        if self.single:
            c = await self.conn
            return await c.executemany(sql, *args, **kwargs)
        p = await self.pool
        return await p.executemany(sql, *args, **kwargs)
