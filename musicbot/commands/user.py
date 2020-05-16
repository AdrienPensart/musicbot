import logging
import json
import click
from prettytable import PrettyTable
from musicbot import helpers
from musicbot.user import User, register_options, auth_options, login_options
from musicbot.admin import Admin, graphql_admin_option
from musicbot.config import config

logger = logging.getLogger(__name__)


@click.group(help='User management', cls=helpers.GroupWithHelp)
def cli():
    pass


@cli.command('list', help='List users (admin)')
@helpers.add_options(helpers.output_option + graphql_admin_option)
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
@helpers.add_options(register_options + helpers.save_option)
def register(save, **kwargs):
    u = User.register(**kwargs)
    if u.token and save:
        logger.info("saving user infos")
        config.configfile['musicbot']['email'] = u.email
        config.configfile['musicbot']['password'] = u.password
        config.configfile['musicbot']['token'] = u.token
        config.write()


@cli.command(aliases=['delete', 'remove'], help='Remove a user')
@helpers.add_options(auth_options)
def unregister(**kwargs):
    u = User(**kwargs)
    u.unregister()


@cli.command(aliases=['token'], help='Authenticate user')
@helpers.add_options(login_options + helpers.save_option)
def login(save, **kwargs):
    u = User(**kwargs)
    print(u.token)
    if u.token and save:
        logger.info("saving user infos")
        config.configfile['musicbot']['token'] = u.token
        config.write()
