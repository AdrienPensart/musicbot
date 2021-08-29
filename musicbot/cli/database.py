import click
from musicbot.database import DEFAULT_DB_ADMIN, DEFAULT_DB_ADMIN_PASSWORD


dsn_argument = click.argument('dsn')
admin_option = click.option('--admin', default=DEFAULT_DB_ADMIN)
password_option = click.option('--password', default=DEFAULT_DB_ADMIN_PASSWORD)
