import click
from . import helpers

MB_TOKEN = 'MB_TOKEN'
MB_SECRET = 'MB_SECRET'
MB_EMAIL = 'MB_EMAIL'
MB_PASSWORD = 'MB_PASSWORD'
MB_FIRST_NAME = 'MB_FIRST_NAME'
MB_LAST_NAME = 'MB_LAST_NAME'

DEFAULT_TOKEN = ''
DEFAULT_SECRET = 'my_little_secret'
DEFAULT_EMAIL = 'admin@musicbot.ovh'
DEFAULT_PASSWORD = helpers.random_password(size=10)
DEFAULT_FIRST_NAME = 'admin'
DEFAULT_LAST_NAME = 'admin'

email_argument = [click.argument('email')]
password_argument = [click.argument('password')]
secret_argument = [click.argument('secret')]

secret_option = [click.option('--secret', envvar=MB_SECRET, help='Secret to sign tokens', default=DEFAULT_SECRET, show_default=False)]
token_option = [click.option('--token', envvar=MB_TOKEN, help='User token', default=DEFAULT_TOKEN, show_default=False)]
email_option = [click.option('--email', envvar=MB_EMAIL, help='User email', default=DEFAULT_EMAIL, show_default=True)]
password_option = [click.option('--password', envvar=MB_PASSWORD, help='User password', default=DEFAULT_PASSWORD, show_default=False)]

options = email_option + password_option + [
    click.option('--first-name', envvar=MB_FIRST_NAME, help='User first name', default=DEFAULT_FIRST_NAME, show_default=True),
    click.option('--last-name', envvar=MB_LAST_NAME, help='User last name', default=DEFAULT_FIRST_NAME, show_default=True)
]
