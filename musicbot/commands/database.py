from typing import List
import logging
import click
from click_skeleton import AdvancedGroup
from beartype import beartype
from musicbot.cli.options import dry_option, yes_option
from musicbot.cli.database import admin_option, password_option, dsn_argument
from musicbot.database import Database

logger = logging.getLogger(__name__)


@click.group(cls=AdvancedGroup, aliases=['db'])
@beartype
def cli() -> None:
    '''Database management (admin)'''


@cli.command('cli', context_settings=dict(ignore_unknown_options=True))
@click.argument('pgcli_args', nargs=-1, type=click.UNPROCESSED)
@beartype
def _pgcli(db: str, pgcli_args: List[str]) -> None:
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
@beartype
def create_role_and_database(dsn: str, admin: str, password: str) -> None:
    '''Create role and database'''
    database = Database(dsn=dsn)
    database.create_role_and_database(admin_user=admin, admin_password=password)


@cli.command(aliases=['drop-db'])
@dsn_argument
@dry_option
@yes_option
@beartype
def drop_database(dsn: str) -> None:
    '''Create role and database'''
    database = Database(dsn=dsn)
    database.drop_schemas()
    database.drop_database()


@cli.command()
@dsn_argument
@dry_option
@beartype
def create_schemas(dsn: str) -> None:
    '''Create database and load schema'''
    database = Database(dsn=dsn)
    database.create_schemas()


@cli.command()
@yes_option
@dry_option
@dsn_argument
@beartype
def drop_schemas(dsn: str) -> None:
    '''Drop database'''
    database = Database(dsn=dsn)
    database.drop_schemas()


@cli.command(aliases=['recreate'])
@yes_option
@dry_option
@dsn_argument
@beartype
def clear_schemas(dsn: str) -> None:
    '''Drop and recreate database and schema'''
    database = Database(dsn=dsn)
    database.clear_schemas()
