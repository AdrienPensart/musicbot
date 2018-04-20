# -*- coding: utf-8 -*-
import click
import sys
import os
import asyncio
from tqdm import tqdm
from logging import error, debug, info
from lib import helpers, lib, collection, database, mfilter
from lib.config import config
from lib.helpers import watcher, fullscan
from lib.lib import empty_dirs


@click.group(invoke_without_command=False)
@helpers.add_options(database.options)
@click.pass_context
def cli(ctx, **kwargs):
    '''Folder scanning'''
    lib.raise_limits()
    ctx.obj.db = collection.Collection(**kwargs)


@cli.command()
@helpers.coro
@click.argument('folders', nargs=-1)
@click.pass_context
async def new(ctx, folders, **kwargs):
    '''Add a new folder in database'''
    tasks = [asyncio.ensure_future(ctx.obj.db.new_folder(f)) for f in folders]
    await asyncio.gather(*tasks)


@cli.command()
@helpers.coro
@click.pass_context
async def list(ctx, **kwargs):
    '''List existing folders'''
    folders = await ctx.obj.db.folders()
    for f in folders:
        print(f['name'])


@cli.command()
@helpers.coro
@helpers.add_options(helpers.concurrency)
@click.option('--crawl', envvar='MB_CRAWL', help='Crawl youtube', is_flag=True)
#@click.option('--sync', envvar='MB_SYNC', help='Call DB synchronously', is_flag=True)
@click.argument('folders', nargs=-1)
@click.pass_context
async def scan(ctx, concurrency, crawl, folders, **kwargs):
    '''Load musics files in database'''
    debug('Concurrency: {}'.format(concurrency))
    await fullscan(ctx.obj.db, folders=folders, concurrency=concurrency, crawl=crawl)


#@cli.command()
#@helpers.coro
#@helpers.add_options(helpers.concurrency)
#@click.argument('folders', nargs=-1)
#@click.pass_context
#async def insert(ctx, concurrency, folders, **kwargs):
#    '''Fast insert of musics files in database'''
#    from lib.lib import find_files
#    from lib.mfilter import Filter, supported_formats
#    from lib.file import File
#    import asyncpg
#    files = [f for f in find_files(folders) if f[1].endswith(tuple(supported_formats))]
#    await ctx.obj.db.execute('DELETE FROM music')
#    await ctx.obj.db.execute('SET synchronous_commit TO OFF')
#    sql = '''insert into music as m (title, album, genre, artist, folder, youtube, number, path, rating, duration, size, keywords) values ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)'''
#    with tqdm(total=len(files), file=sys.stdout, desc="Loading music", leave=True, position=0, disable=config.quiet) as bar:
#        connection = await ctx.obj.db.connect()
#        async def insert(semaphore, f):
#            async with semaphore:
#                m = File(f[1], f[0])
#                try:
#                    l = m.to_tuple()
#                    await connection.execute(sql, *l)
#                except asyncpg.exceptions.CheckViolationError as e:
#                    warning("Violation: {}".format(e))
#                bar.update(1)
#        semaphore = asyncio.BoundedSemaphore(concurrency)
#        tasks = [asyncio.ensure_future(insert(semaphore, f)) for f in files]
#        await asyncio.gather(*tasks)
#
#
#@cli.command()
#@click.argument('folders', nargs=-1)
#@click.pass_context
#def insert2(ctx, folders, **kwargs):
#    '''Fast insert of musics files in database'''
#    from lib.lib import find_files
#    from lib.mfilter import Filter, supported_formats
#    from lib.file import File
#    import psycopg2
#    with psycopg2.connect(ctx.obj.db.connection_string) as conn:
#        with conn.cursor() as cur:
#            cur.execute('DELETE FROM music')
#            sql = '''insert into music as m (title, album, genre, artist, folder, youtube, number, path, rating, duration, size, keywords) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
#            files = [f for f in find_files(folders) if f[1].endswith(tuple(supported_formats))]
#            with tqdm(total=len(files), file=sys.stdout, desc="Loading music", leave=True, position=0, disable=config.quiet) as bar:
#                for f in files:
#                    m = File(f[1], f[0])
#                    cur.execute(sql, m.to_tuple())
#                    bar.update(1)
#
#
#@cli.command()
#@click.argument('folders', nargs=-1)
#@click.pass_context
#def insert3(ctx, folders, **kwargs):
#    '''Fast insert of musics files in database'''
#    from lib.lib import find_files
#    from lib.mfilter import Filter, supported_formats
#    from lib.file import File
#    import psycopg2
#    from psycopg2.extras import execute_values
#    with psycopg2.connect(ctx.obj.db.connection_string) as conn:
#        with conn.cursor() as cur:
#            cur.execute('DELETE FROM music')
#            files = [f for f in find_files(folders) if f[1].endswith(tuple(supported_formats))]
#            data = []
#            for f in files:
#                m = File(f[1], f[0])
#                data.append(m.to_tuple())
#                m.close()
#            sql = '''insert into music as m (title, album, genre, artist, folder, youtube, number, path, rating, duration, size, keywords) values %s'''
#            execute_values(cur, sql, data)
#
#
#@cli.command()
#@click.argument('folders', nargs=-1)
#@click.pass_context
#def insert4(ctx, folders, **kwargs):
#    '''Fast insert of musics files in database'''
#    from lib.lib import find_files
#    from lib.mfilter import Filter, supported_formats
#    from lib.file import File
#    import psycopg2
#    from psycopg2.extras import execute_batch
#    with psycopg2.connect(ctx.obj.db.connection_string) as conn:
#        with conn.cursor() as cur:
#            cur.execute('DELETE FROM music')
#            files = [f for f in find_files(folders) if f[1].endswith(tuple(supported_formats))]
#            data = []
#            for f in files:
#                m = File(f[1], f[0])
#                data.append(m.to_tuple())
#                m.close()
#            sql = '''select * from upsert_one (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
#            execute_batch(cur, sql, data)
#
#
#@cli.command()
#@click.argument('folders', nargs=-1)
#@click.pass_context
#def insert5(ctx, folders, **kwargs):
#    '''Fast insert of musics files in database'''
#    from lib.lib import find_files
#    from lib.mfilter import Filter, supported_formats
#    from lib.file import File
#    import psycopg2
#    from psycopg2.extras import execute_batch
#    with psycopg2.connect(ctx.obj.db.connection_string) as conn:
#        with conn.cursor() as cur:
#            files = [f for f in find_files(folders) if f[1].endswith(tuple(supported_formats))]
#            data = []
#            for f in files:
#                m = File(f[1], f[0])
#                data.append(m.to_tuple())
#                m.close()
#                #break
#            #sql = '''select * from upsert_one (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
#            #cur.execute("PREPARE myupsert AS select * from upsert_one ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)")
#            cur.execute("PREPARE myupsert AS select * from upsert(new_music($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12))")
#            sql = '''EXECUTE myupsert (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
#            execute_batch(cur, sql, data)
#            cur.execute("DEALLOCATE myupsert")
#
#
#@cli.command()
#@click.pass_context
#def test(ctx):
#    '''Fast insert of musics files in database'''
#    from lib.lib import find_files
#    from lib.mfilter import Filter, supported_formats
#    from lib.file import File
#    import psycopg2
#    from psycopg2.extras import execute_batch
#    with psycopg2.connect(ctx.obj.db.connection_string) as conn:
#        with conn.cursor() as cur:
#            sql = '''
#    select 
#        id,
#        title,
#        album,
#        genre,
#        artist,
#        folder,
#        youtube,
#        number,
#        path,
#        rating,
#        duration,
#        size,
#        keywords
#    from music mv
#    where
#        (array_length(%(artists)s::text[], 1) is null or mv.artist = any(%(artists)s::text[])) and
#        (array_length(%(no_artists)s::text[], 1) is null or not (mv.artist = any(%(no_artists)s::text[]))) and
#        (array_length(%(albums)s::text[], 1) is null or mv.album = any(%(albums)s::text[])) and
#        (array_length(%(no_albums)s::text[], 1) is null or not (mv.album = any(%(no_albums)s::text[]))) and
#        (array_length(%(titles)s::text[], 1) is null or mv.title = any(%(titles)s::text[])) and
#        (array_length(%(no_titles)s::text[], 1) is null or not (mv.title = any(%(no_titles)s::text[]))) and
#        (array_length(%(genres)s::text[], 1) is null or mv.genre = any(%(genres)s::text[])) and
#        (array_length(%(no_genres)s::text[], 1) is null or not (mv.genre = any(%(no_genres)s::text[]))) and
#        (array_length(%(keywords)s::text[], 1) is null or %(keywords)s::text[] <@ mv.keywords) and
#        (array_length(%(no_keywords)s::text[], 1) is null or not (%(no_keywords)s::text[] && mv.keywords)) and
#        (array_length(%(formats)s::text[], 1) is null or mv.path similar to '%%.(' || array_to_string(%(formats)s::text[], '|') || ')') and
#        (array_length(%(no_formats)s::text[], 1) is null or mv.path not similar to '%%.(' || array_to_string(%(no_formats)s::text[], '|') || ')') and
#        mv.duration between %(min_duration)s and %(max_duration)s and
#        mv.size between %(min_size)s and %(max_size)s and
#        mv.rating between %(min_rating)s and %(max_rating)s and
#        (%(youtube)s is null or (%(youtube)s = mv.youtube))
#    order by
#        case when(%(shuffle)s = 'true') then random() end,
#        case when(%(shuffle)s = 'false') then artist end,
#        case when(%(shuffle)s = 'false') then album end,
#        case when(%(shuffle)s = 'false') then number end
#    limit %(limit)s
#'''
#            data = {'min_duration':0, 'max_duration':2147483647, 'min_size':0, 'max_size':2147483647, 'min_rating':0, 'max_rating':5, 'artists':[], 'no_artists':[], 'albums':[], 'no_albums':[], 'titles':[], 'no_titles':[], 'genres':[], 'no_genres':[], 'formats':[], 'no_formats':[], 'keywords':['best'], 'no_keywords':[], 'shuffle':True, 'relative':False, 'limit':2147483647, 'youtube': None}
#            cur.execute(sql, data)
#            print(cur.query.decode('utf-8'))


@cli.command()
@helpers.coro
@helpers.add_options(helpers.concurrency)
@click.option('--crawl', envvar='MB_CRAWL', help='Crawl youtube', is_flag=True)
@click.pass_context
async def rescan(ctx, concurrency, crawl, **kwargs):
    '''Rescan all folders registered in database'''
    debug('Concurrency: {}'.format(concurrency))
    # Should upsert
    await fullscan(ctx.obj.db, concurrency=concurrency, crawl=crawl)


@cli.command()
@helpers.coro
@click.pass_context
async def watch(ctx, **kwargs):
    '''Watch files changes in folders'''
    await watcher(ctx.obj.db)


@cli.command()
@click.argument('folders', nargs=-1)
@click.pass_context
def find(ctx, folders, **kwargs):
    '''Only list files in selected folders'''
    files = lib.find_files(folders)
    for f in files:
        print(f[1])


@cli.command()
@helpers.coro
@helpers.add_options(mfilter.options)
@click.argument('destination')
@click.pass_context
async def sync(ctx, destination, **kwargs):
    '''Copy selected musics with filters to destination folder'''
    info('Destination: {}'.format(destination))
    ctx.obj.mf = mfilter.Filter(**kwargs)
    musics = await ctx.obj.db.musics(ctx.obj.mf)

    files = lib.all_files(destination)
    destinations = {f[len(destination) + 1:]: f for f in files}
    sources = {m['path'][len(m['folder']) + 1:]: m['path'] for m in musics}
    to_delete = set(destinations.keys()) - set(sources.keys())
    to_copy = set(sources.keys()) - set(destinations.keys())
    with tqdm(total=len(to_delete), file=sys.stdout, desc="Deleting music", leave=True, position=0, disable=config.quiet) as bar:
        for d in to_delete:
            if not config.dry:
                try:
                    info("Deleting {}".format(destinations[d]))
                    os.remove(destinations[d])
                except Exception as e:
                    error(e)
            else:
                info("[DRY-RUN] False Deleting {}".format(destinations[d]))
            bar.update(1)
    with tqdm(total=len(to_copy), file=sys.stdout, desc="Copying music", leave=True, position=0, disable=config.quiet) as bar:
        from shutil import copyfile
        for c in sorted(to_copy):
            final_destination = os.path.join(destination, c)
            if not config.dry:
                info("Copying {} to {}".format(sources[c], final_destination))
                os.makedirs(os.path.dirname(final_destination), exist_ok=True)
                copyfile(sources[c], final_destination)
            else:
                info("[DRY-RUN] False Copying {} to {}".format(sources[c], final_destination))
            bar.update(1)

    import shutil
    for d in empty_dirs(destination):
        if not config.dry:
            shutil.rmtree(d)
        info("[DRY-RUN] Removing empty dir {}".format(d))
