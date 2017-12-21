# -*- coding: utf-8 -*-
import click
from lib import youtube, helpers, database, filter
from logging import debug
from tqdm import tqdm


@click.group()
@helpers.add_options(database.options)
@click.pass_context
def cli(ctx, **kwargs):
    '''Youtube management'''
    ctx.obj.db = database.DbContext(**kwargs)


@cli.command()
@click.pass_context
@helpers.coro
@helpers.add_options(filter.options)
async def sync(ctx, **kwargs):
    '''Fetch youtube links for each music'''
    ctx.obj.mf = filter.Filter(**kwargs)
    musics = await ctx.obj.db.filter(ctx.obj.mf)
    with tqdm(desc='Youtube crawling', total=len(musics), disable=ctx.obj.config.quiet) as bar:
        for m in musics:
            bar.update(1)
            result = youtube.search(m['artist'], m['title'], m['duration'])
            debug(m['artist'], m['title'], m['duration'], result)
            await ctx.obj.db.set_youtube(m['path'], result)

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
