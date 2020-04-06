import logging
import json
import click
from prettytable import PrettyTable
from musicbot import helpers, user
from musicbot.config import config

logger = logging.getLogger(__name__)


@click.group(cls=helpers.GroupWithHelp)
def cli():
    '''User management'''


@cli.command('list')
@helpers.add_options(helpers.output_option + user.graphql_admin_option)
def _list(graphql_admin, output):
    '''List users (admin)'''
    a = user.Admin(graphql=graphql_admin)
    users = a.users()
    if output == 'table':
        pt = PrettyTable()
        pt.field_names = ["Email", "Firstname", "Lastname", "Created at", "Updated at"]
        for u in users:
            pt.add_row([u["accountByUserId"]["email"], u["firstName"], u["lastName"], u["createdAt"], u["updatedAt"]])
        print(pt)
    elif output == 'json':
        print(json.dumps(users))


@cli.command(aliases=['new', 'add', 'create'])
@helpers.add_options(user.register_options + helpers.save_option)
def register(save, **kwargs):
    '''Register a new user'''
    u = user.User.register(**kwargs)
    if u.token and save:
        logger.info("saving user infos")
        config.configfile['DEFAULT']['email'] = u.email
        config.configfile['DEFAULT']['password'] = u.password
        config.configfile['DEFAULT']['token'] = u.token
        config.write()


@cli.command(aliases=['delete', 'remove'])
@helpers.add_options(user.auth_options)
def unregister(**kwargs):
    '''Remove a user'''
    u = user.User(**kwargs)
    u.unregister()


@cli.command(aliases=['token'])
@helpers.add_options(user.login_options + helpers.save_option)
def login(save, **kwargs):
    '''Authenticate user'''
    u = user.User(**kwargs)
    print(u.token)
    if u.token and save:
        logger.info("saving user infos")
        config.configfile['DEFAULT']['token'] = u.token
        config.write()
