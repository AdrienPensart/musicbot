import click
from . import helpers

MB_TOKEN = 'MB_TOKEN'
DEFAULT_TOKEN = ''
token_argument = [click.argument('token')]
token_option = [click.option('--token', envvar=MB_TOKEN, help='User token', default=DEFAULT_TOKEN, show_default=False)]

MB_SECRET = 'MB_SECRET'
DEFAULT_SECRET = 'my_little_secret'
secret_argument = [click.argument('secret')]
secret_option = [click.option('--secret', envvar=MB_SECRET, help='Secret to sign tokens', default=DEFAULT_SECRET, show_default=False)]

MB_EMAIL = 'MB_EMAIL'
DEFAULT_EMAIL = 'admin@musicbot.ovh'
email_argument = [click.argument('email')]
email_option = [click.option('--email', envvar=MB_EMAIL, help='User email', default=DEFAULT_EMAIL, show_default=True)]

MB_PASSWORD = 'MB_PASSWORD'
DEFAULT_PASSWORD = helpers.random_password(size=10)
password_argument = [click.argument('password')]
password_option = [click.option('--password', envvar=MB_PASSWORD, help='User password', default=DEFAULT_PASSWORD, show_default=False)]

MB_FIRST_NAME = 'MB_FIRST_NAME'
DEFAULT_FIRST_NAME = 'admin'
first_name_option = [click.option('--first-name', envvar=MB_FIRST_NAME, help='User first name', default=DEFAULT_FIRST_NAME, show_default=True)]

MB_LAST_NAME = 'MB_LAST_NAME'
DEFAULT_LAST_NAME = 'admin'
last_name_option = [click.option('--last-name', envvar=MB_LAST_NAME, help='User last name', default=DEFAULT_FIRST_NAME, show_default=True)]

MB_GRAPHQL = 'MB_GRAPHQL'
DEFAULT_GRAPHQL = 'http://127.0.0.1:5000/graphql'
graphql_option = [click.option('--graphql', envvar=MB_GRAPHQL, help='GraphQL endpoint', default=DEFAULT_GRAPHQL, show_default=True)]

options = email_option + password_option + first_name_option + last_name_option + graphql_option
