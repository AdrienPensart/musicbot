# -*- coding: utf-8 -*-
import click
import asyncio
import asyncpg
from logging import debug
from lib import helpers


@click.group(invoke_without_command=False)
@helpers.add_options(helpers.db_options)
@helpers.global_context
@helpers.db_context
def cli(dbctx, gctx, host, port, user, password, db, **kwargs):
    debug('db cli')
    dbctx.host = host
    dbctx.port = port
    dbctx.user = user
    dbctx.password = password
    dbctx.db = db
    debug(dbctx)
    debug(gctx)
    debug(dbctx.connection_string())


@cli.command()
@helpers.global_context
@helpers.db_context
def create(dbctx, gctx, **kwargs):
    debug('db create')
    debug(kwargs)

    async def main():
        conn = await asyncpg.connect(dbctx.connection_string())
        musics = await conn.fetch('select * from musics limit 2')
        for m in musics:
            print(m)

        await conn.close()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()


@cli.command()
@helpers.global_context
@helpers.db_context
def drop(ctx, **kwargs):
    click.echo('drop')


@cli.command()
@helpers.global_context
@helpers.db_context
def clear(ctx, **kwargs):
    click.echo('clear')


@cli.command()
@helpers.global_context
@helpers.db_context
def clean(ctx, **kwargs):
    click.echo('clean')
