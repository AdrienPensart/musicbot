import logging
import click
from click_skeleton import AdvancedGroup
from musicbot.cli.options import dry_option, yes_option
from musicbot.cli.database import admin_option, password_option, dsn_argument
from musicbot.database import Database

logger = logging.getLogger(__name__)


@click.group(cls=AdvancedGroup, aliases=['db'])
def cli():
    '''Database management (admin)'''


@cli.command('cli', context_settings=dict(ignore_unknown_options=True))
@click.argument('pgcli_args', nargs=-1, type=click.UNPROCESSED)
def _pgcli(db, pgcli_args):
    '''Start PgCLI util'''
    from subprocess import call
    cmdline = ['pgcli', db] + list(pgcli_args)
    joined_cmdline = ' '.join(cmdline)
    click.echo(f'Invoking: {joined_cmdline}')
    call(cmdline)


@cli.command(aliases=['create-role-and-db'])
@dsn_argument
@dry_option
@admin_option
@password_option
def create_role_and_database(dsn, admin, password):
    '''Create role and database'''
    database = Database(dsn=dsn)
    database.create_role_and_database(admin_user=admin, admin_password=password)


@cli.command(aliases=['drop-db'])
@dsn_argument
@dry_option
@yes_option
def drop_database(dsn):
    '''Create role and database'''
    database = Database(dsn=dsn)
    database.drop_schemas()
    database.drop_database()


@cli.command()
@dsn_argument
@dry_option
def create_schemas(dsn):
    '''Create database and load schema'''
    database = Database(dsn=dsn)
    database.create_schemas()


@cli.command()
@yes_option
@dry_option
@dsn_argument
def drop_schemas(dsn):
    '''Drop database'''
    database = Database(dsn=dsn)
    database.drop_schemas()


@cli.command(aliases=['recreate'])
@yes_option
@dry_option
@dsn_argument
def clear_schemas(dsn):
    '''Drop and recreate database and schema'''
    database = Database(dsn=dsn)
    database.clear_schemas()
