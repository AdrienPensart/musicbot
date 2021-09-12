import logging
import json
from prettytable import PrettyTable  # type: ignore
from click_option_group import optgroup  # type: ignore
from click_skeleton import AdvancedGroup
import click
from musicbot.cli.options import output_option, save_option
from musicbot.cli.user import (
    user_options,
    graphql_option,
    email_option,
    password_option,
    first_name_option,
    last_name_option,
)
from musicbot.cli.admin import admin_options
from musicbot.user import User
from musicbot.admin import Admin
from musicbot.object import MusicbotObject

logger = logging.getLogger(__name__)


@click.group(help='User management', cls=AdvancedGroup)
def cli():
    pass


@cli.command('list', help='List users (admin)')
@output_option
@admin_options
def _list(graphql_admin: Admin, output: str, **kwargs):
    admin = Admin.from_auth(graphql=graphql_admin, **kwargs)
    users = admin.users()
    if output == 'table':
        pt = PrettyTable(["ID", "Email", "Firstname", "Lastname", "Created at", "Updated at"])
        for u in users:
            pt.add_row([u["id"], u["email"], u["firstName"], u["lastName"], u["createdAt"], u["updatedAt"]])
        print(pt)
    elif output == 'json':
        print(json.dumps(users))


@cli.command(aliases=['new', 'add', 'create'], help='Register a new user')
@save_option
@optgroup('Register options')
@graphql_option
@email_option
@password_option
@first_name_option
@last_name_option
def register(save: bool, email: str, password: str, **kwargs):
    user = User.register(email=email, password=password, **kwargs)
    if not user.token:
        logger.error('register failed')
        return
    if save:
        logger.info("saving user infos")
        MusicbotObject.config.configfile['musicbot']['email'] = email
        MusicbotObject.config.configfile['musicbot']['password'] = password
        MusicbotObject.config.configfile['musicbot']['token'] = user.token
        MusicbotObject.config.write()


@cli.command(aliases=['delete', 'remove'], help='Remove a user')
@user_options
def unregister(user: User):
    user.unregister()


@cli.command(help='Info about me')
@user_options
def whoami(user: User):
    print(user.whoami());


@cli.command(aliases=['token'], help='Authenticate user')
@save_option
@optgroup('Login options')
@graphql_option
@email_option
@password_option
def login(save: bool, **kwargs):
    user = User.from_auth(**kwargs)
    print(user.token)
    if save:
        logger.info("saving user infos")
        MusicbotObject.config.configfile['musicbot']['token'] = user.token
        MusicbotObject.config.write()
