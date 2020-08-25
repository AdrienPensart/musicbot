import logging
import json
import click
from prettytable import PrettyTable
from musicbot import helpers
from musicbot.click_helpers import AdvancedGroup, add_options
from musicbot.user import User, register_options, auth_options, login_options
from musicbot.admin import Admin, graphql_admin_option
from musicbot.config import config

logger = logging.getLogger(__name__)


@click.group(help='User management', cls=AdvancedGroup)
def cli():
    pass


@cli.command('list', help='List users (admin)')
@add_options(
    helpers.output_option +
    graphql_admin_option
)
def _list(graphql_admin, output):
    a = Admin(graphql=graphql_admin)
    users = a.users()
    if output == 'table':
        pt = PrettyTable()
        pt.field_names = ["Email", "Firstname", "Lastname", "Created at", "Updated at"]
        for u in users:
            pt.add_row([u["email"], u["user"]["firstName"], u["user"]["lastName"], u["user"]["createdAt"], u["user"]["updatedAt"]])
        print(pt)
    elif output == 'json':
        print(json.dumps(users))


@cli.command(aliases=['new', 'add', 'create'], help='Register a new user')
@add_options(
    helpers.save_option +
    register_options
)
def register(save, **kwargs):
    u = User.register(**kwargs)
    if u.token and save:
        logger.info("saving user infos")
        config.configfile['musicbot']['email'] = u.email
        config.configfile['musicbot']['password'] = u.password
        config.configfile['musicbot']['token'] = u.token
        config.write()


@cli.command(aliases=['delete', 'remove'], help='Remove a user')
@add_options(auth_options)
def unregister(**kwargs):
    u = User(**kwargs)
    u.unregister()


@cli.command(aliases=['token'], help='Authenticate user')
@add_options(
    helpers.save_option +
    login_options
)
def login(save, **kwargs):
    u = User(**kwargs)
    print(u.token)
    if u.token and save:
        logger.info("saving user infos")
        config.configfile['musicbot']['token'] = u.token
        config.write()
