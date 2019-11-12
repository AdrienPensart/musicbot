import logging
import click
from musicbot import helpers, user

logger = logging.getLogger(__name__)


@click.group(cls=helpers.GroupWithHelp)
def cli():
    '''User management'''


@cli.command('list')
@helpers.add_options(user.graphql_admin_option)
def _list(graphql_admin):
    '''List users (admin)'''
    a = user.Admin(graphql=graphql_admin)
    for u in a.users():
        print(u["accountByUserId"]["email"], u["firstName"], u["lastName"], u["createdAt"], u["updatedAt"])


@cli.command(aliases=['new', 'add', 'create'])
@helpers.add_options(user.options)
def register(**kwargs):
    '''Register a new user'''
    user.User.register(**kwargs)


@cli.command(aliases=['delete', 'remove'])
@helpers.add_options(user.auth_options)
def unregister(**kwargs):
    '''Remove a user'''
    u = user.User(**kwargs)
    u.unregister()


@cli.command(aliases=['token'])
@helpers.add_options(user.auth_options)
def login(**kwargs):
    '''Authenticate user'''
    u = user.User(**kwargs)
    print(u.token)
