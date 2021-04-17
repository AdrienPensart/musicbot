from click_option_group import optgroup, AllOptionGroup  # type: ignore
from click_skeleton import add_options
from musicbot.admin import DEFAULT_GRAPHQL_ADMIN, DEFAULT_GRAPHQL_ADMIN_USER, DEFAULT_GRAPHQL_ADMIN_PASSWORD
from musicbot.cli.options import config_string

graphql_admin_option = optgroup.option(
    '--graphql-admin',
    help='GraphQL endpoint',
    default=DEFAULT_GRAPHQL_ADMIN,
    callback=config_string,
    show_default=True,
)

graphql_admin_user_option = optgroup.option(
    '--graphql-admin-user',
    help='GraphQL admin user (basic auth)',
    default=DEFAULT_GRAPHQL_ADMIN_USER,
    callback=config_string,
)

graphql_admin_password_option = optgroup.option(
    '--graphql-admin-password',
    help='GraphQL admin password (basic auth)',
    default=DEFAULT_GRAPHQL_ADMIN_PASSWORD,
    callback=config_string,
)

admin_options = add_options(
    optgroup.group('Admin options'),
    graphql_admin_option,
    optgroup.group('Basic auth', cls=AllOptionGroup),
    graphql_admin_user_option,
    graphql_admin_password_option,
)
