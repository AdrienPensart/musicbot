# -*- coding: utf-8 -*-
import click
from lib import filter, helpers, database


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx, **kwargs):
    pass


@cli.command()
@helpers.coro
@click.pass_context
@helpers.add_options(filter.options)
async def errors(ctx, **kwargs):
    ctx.obj.db = database.DbContext(**kwargs)
    mf = filter.Filter(**kwargs)
    errors = await ctx.obj.db.errors(mf)
    for e in errors:
        print(e)
