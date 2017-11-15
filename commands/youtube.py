# -*- coding: utf-8 -*-
import click
from lib import youtube, helpers, database, options
from lib.filter import Filter
from multiprocessing.pool import ThreadPool
from logging import debug
from tqdm import tqdm


@click.pass_context
def cli(ctx, **kwargs):
    ctx.obj.db = database.DbContext(**kwargs)


@cli.command()
@click.pass_context
@helpers.coro
@options.add_options(options.filters)
async def sync(ctx, **kwargs):
    ctx.obj.mf = Filter(**kwargs)
    musics = await ctx.obj.db.filter(ctx.obj.mf)
    with tqdm(desc='Youtube crawling', total=len(musics), disable=ctx.obj.config.quiet) as bar:
        def search_local(m):
            bar.update(1)
            m = dict(m)
            result = youtube.search(m['artist'], m['title'], m['duration'])
            m['youtube'] = result
            debug(m['artist'], m['title'], m['duration'], m['youtube'])
            return m
        pool = ThreadPool(1)
        musics = pool.imap_unordered(search_local, musics)
        await ctx.obj.db.upsertall(musics)
