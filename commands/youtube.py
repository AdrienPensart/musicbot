# -*- coding: utf-8 -*- import click
import click
import asyncio
from tqdm import tqdm
from lib import youtube, helpers, database, collection, filter

options = [
    click.option('--concurrency', envvar='MB_CONCURRENCY', help='Number of coroutines', default=32),
]


@click.group()
@helpers.add_options(database.options)
@helpers.add_options(filter.options)
@helpers.add_options(options)
@click.pass_context
def cli(ctx, concurrency, **kwargs):
    '''Youtube management'''
    ctx.obj.db = collection.Collection(**kwargs)
    ctx.obj.mf = filter.Filter(**kwargs)
    ctx.obj.concurrency = concurrency


@cli.command()
@click.pass_context
@helpers.coro
async def musics(ctx, **kwargs):
    '''Fetch youtube links for each music'''
    if ctx.obj.mf.youtube is None:
        ctx.obj.mf.youtube = ''
    musics = await ctx.obj.db.filter(ctx.obj.mf)
    with tqdm(desc='Youtube musics', total=len(musics), disable=ctx.obj.config.quiet) as bar:
        async def search(semaphore, m):
            async with semaphore:
                result = await youtube.search(m['artist'], m['title'], m['duration'])
                await ctx.obj.db.set_music_youtube(m['path'], result)
                bar.update(1)
        semaphore = asyncio.BoundedSemaphore(ctx.obj.concurrency)
        requests = [asyncio.ensure_future(search(semaphore, m)) for m in musics]
        await asyncio.gather(*requests)


@cli.command()
@click.pass_context
@helpers.coro
@click.option('--youtube-album', envvar='MB_YOUTUBE_ALBUM', help='Select albums with a youtube link', default='')
async def albums(ctx, youtube_album, **kwargs):
    '''Fetch youtube links for each album'''
    albums = await ctx.obj.db.albums(ctx.obj.mf, youtube_album)
    with tqdm(desc='Youtube albums', total=len(albums), disable=ctx.obj.config.quiet) as bar:
        async def search(semaphore, a):
            async with semaphore:
                result = await youtube.search(a['artist'], a['name'] + ' full album', a['duration'])
                await ctx.obj.db.set_album_youtube(a['id'], result)
                bar.update(1)
        semaphore = asyncio.BoundedSemaphore(ctx.obj.concurrency)
        requests = [asyncio.ensure_future(search(semaphore, a)) for a in albums]
        await asyncio.gather(*requests)
