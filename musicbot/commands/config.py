import click
from logging_tree import printout
from musicbot.lib import helpers
from musicbot.lib.config import config


@click.group(cls=helpers.GroupWithHelp)
def cli():
    '''Config management'''


@cli.command()
def show():
    '''Print default config'''
    print(config)


# from lib.web import app
# from lib import database
# @cli.command()
# @helpers.coro
# @helpers.add_options(persistence.options)
# @helpers.add_options(database.options)
# @helpers.add_options(app.options)
# async def save(**kwargs):
#     '''Save config'''
#     from lib import persistence
#     redis = persistence.Persistence(**kwargs)
#     await redis.connect()
#     await redis.execute('set', 'my-key', 'value')
#     val = await redis.execute('get', 'my-key')
#     print(val)
#     await redis.close()


@cli.command()
def logging():
    '''Show loggers tree'''
    printout()
