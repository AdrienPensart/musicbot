from typing import Any
import click
from click_option_group import optgroup  # type: ignore
from musicbot import defaults
from musicbot.user import User
from musicbot.helpers import config_string


def sane_user(ctx: click.Context, param: Any, value: Any) -> User:  # pylint: disable=unused-argument
    kwargs = {}
    for field in ('token', 'email', 'password', 'graphql'):
        kwargs[field] = ctx.params.get(field, None)
        ctx.params.pop(field, None)
    user = User(**kwargs)
    ctx.params['user'] = user
    return user


email_option = optgroup.option(
    '--email', '-e',
    help='User email',
    default=defaults.DEFAULT_EMAIL,
    is_eager=True,
    callback=config_string,
)

password_option = optgroup.option(
    '--password', '-p',
    help='User password',
    default=defaults.DEFAULT_PASSWORD,
    is_eager=True,
    callback=config_string,
)

first_name_option = optgroup.option(
    '--first-name',
    help='User first name',
    default=defaults.DEFAULT_FIRST_NAME,
    is_eager=True,
    callback=config_string,
    show_default=True,
)

last_name_option = optgroup.option(
    '--last-name',
    help='User last name',
    default=defaults.DEFAULT_FIRST_NAME,
    is_eager=True,
    callback=config_string,
    show_default=True,
)

token_option = optgroup.option(
    '--token', '-t',
    help='User token',
    is_eager=True,
)

graphql_option = optgroup.option(
    '--graphql',
    help='GraphQL endpoint',
    default=defaults.DEFAULT_GRAPHQL,
    is_eager=True,
    callback=config_string,
    show_default=True,
)

user_option = click.option(
    '--user',
    help='Music Filter',
    expose_value=False,
    callback=sane_user,
    hidden=True,
)

register_options = [
    optgroup.group('Register options'),
    graphql_option,
    email_option,
    password_option,
    first_name_option,
    last_name_option,
]

login_options = [
    optgroup.group('User options'),
    graphql_option,
    email_option,
    password_option,
    user_option,
]

auth_options = [
    user_option,
    optgroup.group('Auth options'),
    graphql_option,
    token_option,
    email_option,
    password_option,
]
