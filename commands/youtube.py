# -*- coding: utf-8 -*- import click
import click
from tqdm import tqdm
from lib import youtube, helpers, database, filter
from logging import debug

# options = [
#     click.option('--threads', envvar='MB_THREADS', help='Number of threads', default=32),
# ]


@click.group()
@helpers.add_options(database.options)
@helpers.add_options(filter.options)
# @helpers.add_options(options)
@click.pass_context
# def cli(ctx, threads, **kwargs):
def cli(ctx, **kwargs):
    '''Youtube management'''
    ctx.obj.db = database.DbContext(**kwargs)
    ctx.obj.mf = filter.Filter(**kwargs)
    if ctx.obj.mf.youtube is None:
        ctx.obj.mf.youtube = ''
    # ctx.obj.threads = threads


@cli.command()
@click.pass_context
@helpers.coro
async def musics(ctx, **kwargs):
    '''Fetch youtube links for each music'''
    musics = await ctx.obj.db.filter(ctx.obj.mf)
    with tqdm(desc='Youtube musics', total=len(musics), disable=ctx.obj.config.quiet) as bar:
        for m in musics:
            result = youtube.search(m['artist'], m['title'], m['duration'])
            debug('artist: {} title: {} duration: {} result: {}'.format(m['artist'], m['title'], m['duration'], result))
            await ctx.obj.db.set_music_youtube(m['path'], result)
            bar.update(1)


@cli.command()
@click.pass_context
@helpers.coro
async def albums(ctx, **kwargs):
    '''Fetch youtube links for each album'''
    albums = await ctx.obj.db.albums(ctx.obj.mf)
    with tqdm(desc='Youtube albums', total=len(albums), disable=ctx.obj.config.quiet) as bar:
        for a in albums:
            result = youtube.search(a['artist'], a['name'] + ' full album', a['duration'])
            debug('artist: {} album: {} duration: {} result: {}'.format(a['artist'], a['name'], a['duration'], result))
            await ctx.obj.db.set_album_youtube(a['id'], result)
            bar.update(1)
# async def search_local(m):
#     bar.update(1)
#     m = dict(m)
#     result = youtube.search(m['artist'], m['title'], m['duration'])
#     m['youtube'] = result
#     debug(m['artist'], m['title'], m['duration'], m['youtube'])
#     await ctx.obj.db.upsert(m)
#     return m
# from multiprocessing.pool import ThreadPool
# pool = ThreadPool(1)
# musics = pool.imap_unordered(search_local, musics)
