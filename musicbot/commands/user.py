from typing import Optional
import logging
import json
from rich.table import Table
from click_option_group import optgroup  # type: ignore
from click_skeleton import AdvancedGroup
import click
from beartype import beartype
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
@beartype
def cli() -> None:
    pass


@cli.command('list', help='List users (admin)')
@output_option
@admin_options
@beartype
def _list(graphql_admin: str, output: str, graphql_admin_user: Optional[str], graphql_admin_password: Optional[str]) -> None:
    admin = Admin.from_auth(
        graphql=graphql_admin,
        graphql_admin_user=graphql_admin_user,
        graphql_admin_password=graphql_admin_password,
    )
    users = admin.users()
    if output == 'table':
        table = Table("ID", "Email", "Firstname", "Lastname", "Created at", "Updated at")
        for u in users:
            table.add_row(u["id"], u["email"], u["firstName"], u["lastName"], u["createdAt"], u["updatedAt"])
        MusicbotObject.console.print(table)
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
@beartype
def register(graphql: str, save: bool, email: str, password: str, first_name: str, last_name: str) -> None:
    user = User.register(
        graphql=graphql,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
    )
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
@beartype
def unregister(user: User) -> None:
    user.unregister()


@cli.command(help='Info about me')
@user_options
@beartype
def whoami(user: User) -> None:
    print(user.whoami())


@cli.command(aliases=['token'], help='Authenticate user')
@save_option
@optgroup('Login options')
@graphql_option
@email_option
@password_option
@beartype
def login(save: bool, graphql: str, email: str, password: str) -> None:
    user = User.from_auth(
        graphql=graphql,
        email=email,
        password=password,
    )
    print(user.token)
    if save:
        logger.info("saving user infos")
        MusicbotObject.config.configfile['musicbot']['token'] = user.token
        MusicbotObject.config.write()
