from typing import Any
import click
from click_option_group import optgroup  # type: ignore
from click_skeleton import add_options
from musicbot.user import (
    User,
    DEFAULT_EMAIL,
    DEFAULT_PASSWORD,
    DEFAULT_FIRST_NAME,
    DEFAULT_LAST_NAME,
)
from musicbot.graphql import DEFAULT_GRAPHQL
from musicbot.exceptions import FailedAuthentication
from musicbot.cli.options import config_string


def sane_user(ctx: click.Context, param: Any, value: Any) -> User:  # pylint:disable=unused-argument
    graphql = ctx.params.pop('graphql')
    email = ctx.params.pop('email')
    password = ctx.params.pop('password')
    if value:
        user = User.from_token(graphql=graphql, token=value)
    elif email and password:
        user = User.from_auth(graphql=graphql, email=email, password=password)
    else:
        raise FailedAuthentication("Either token or email/password must be given")
    ctx.params['user'] = user
    return user


token_option = optgroup.option(
    '--token', '-t',
    help='User token',
    expose_value=False,
    callback=sane_user,
)

email_option = optgroup.option(
    '--email', '-e',
    help='User email',
    default=DEFAULT_EMAIL,
    is_eager=True,
    callback=config_string,
)

password_option = optgroup.option(
    '--password', '-p',
    help='User password',
    default=DEFAULT_PASSWORD,
    is_eager=True,
    callback=config_string,
)

first_name_option = optgroup.option(
    '--first-name',
    help='User first name',
    default=DEFAULT_FIRST_NAME,
    is_eager=True,
    callback=config_string,
    show_default=True,
)

last_name_option = optgroup.option(
    '--last-name',
    help='User last name',
    default=DEFAULT_LAST_NAME,
    is_eager=True,
    callback=config_string,
    show_default=True,
)

graphql_option = optgroup.option(
    '--graphql', '-g',
    help='GraphQL endpoint',
    default=DEFAULT_GRAPHQL,
    is_eager=True,
    callback=config_string,
    show_default=True,
)

user_options = add_options(
    optgroup.group('Auth options'),
    graphql_option,
    token_option,
    email_option,
    password_option,
)
