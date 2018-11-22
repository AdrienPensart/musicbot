import click
from musicbot.lib import database, mfilter, helpers


@click.group(cls=helpers.GroupWithHelp)
@click.pass_context
@helpers.coro
@helpers.add_options(database.options)
async def cli(ctx, **kwargs):
    '''Inconsistencies management'''
    ctx.obj.db = await database.Database.make(**kwargs)


@cli.command()
@helpers.coro
@click.pass_context
@helpers.add_options(mfilter.options)
async def errors(ctx, **kwargs):
    '''Detect errors'''
    mf = mfilter.Filter(**kwargs)
    errors = await ctx.obj.db.errors(mf)
    for e in errors:
        print(e)
