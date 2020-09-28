from click_option_group import optgroup, AllOptionGroup  # type: ignore
from musicbot import defaults
from musicbot.helpers import config_string

graphql_admin_option = optgroup.option(
    '--graphql-admin',
    help='GraphQL endpoint',
    default=defaults.DEFAULT_GRAPHQL_ADMIN,
    callback=config_string,
    show_default=True,
)


graphql_admin_user_option = optgroup.option(
    '--graphql-admin-user',
    help='GraphQL admin user (basic auth)',
    default=defaults.DEFAULT_GRAPHQL_ADMIN_USER,
    callback=config_string,
)


graphql_admin_password_option = optgroup.option(
    '--graphql-admin-password',
    help='GraphQL admin password (basic auth)',
    default=defaults.DEFAULT_GRAPHQL_ADMIN_PASSWORD,
    callback=config_string,
)

admin_options = [
    optgroup.group('Admin options'),
    graphql_admin_option,
    optgroup.group('Basic auth', cls=AllOptionGroup),
    graphql_admin_user_option,
    graphql_admin_password_option,
]
