import click
import logging
from musicbot.lib import helpers, database, user

logger = logging.getLogger(__name__)


@click.group(cls=helpers.GroupWithHelp)
@helpers.coro
def cli():
    '''User management'''


@cli.command()
@helpers.coro
@helpers.add_options(database.options)
async def list(**kwargs):
    '''List users (admin)'''
    db = await database.Database.make(**kwargs)
    users = await db.fetch('''select * from musicbot_public.user u inner join musicbot_private.account a on u.id=a.user_id''')
    for u in users:
        print(u)


@cli.command()
@helpers.add_options(user.options)
def register(**kwargs):
    '''Register a new user'''
    user.User.register(**kwargs)


@cli.command()
@helpers.add_options(user.auth_options)
def unregister(**kwargs):
    '''Remove a user'''
    u = user.User(**kwargs)
    u.unregister()


@cli.command()
@helpers.add_options(user.auth_options)
def login(**kwargs):
    '''Authenticate user'''
    u = user.User(**kwargs)
    print(u.token)
