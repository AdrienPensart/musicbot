import click
from lib import database, mfilter, helpers, collection


@click.group(cls=helpers.GroupWithHelp)
@click.pass_context
@helpers.add_options(database.options)
def cli(ctx, **kwargs):
    '''Inconsistencies management'''
    ctx.obj.db = collection.Collection(**kwargs)


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
