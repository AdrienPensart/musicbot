import logging
import json
import click
from click_skeleton import AdvancedGroup
from rich.table import Table
from beartype import beartype
from musicbot.cli.options import output_option
from musicbot.cli.user import user_options
from musicbot.user import User
from musicbot.object import MusicbotObject

logger = logging.getLogger(__name__)


@click.group('filter', help='Filter management', cls=AdvancedGroup)
@beartype
def cli() -> None:
    pass


@cli.command(help='Load default filters', aliases=['load-defaults'])
@user_options
@beartype
def load(user: User) -> None:
    user.load_default_filters()


@cli.command(help='Count filters')
@user_options
@beartype
def count(user: User) -> None:
    print(user.count_filters())


@cli.command('list', help='List filters')
@output_option
@user_options
@beartype
def _list(user: User, output: str) -> None:
    if output == 'json':
        print(json.dumps(user.list_filters()))
    elif output == 'table':
        table = Table("Name", "Keywords", "No keywords", "Min rating", "Max rating")
        for f in user.list_filters():
            table.add_row(f['name'], f['keywords'], f['noKeywords'], f['minRating'], f['maxRating'])
        MusicbotObject.console.print(table)


@cli.command(help='Print a filter', aliases=['get', 'print'])
@output_option
@user_options
@click.argument('name')
@beartype
def show(user: User, name: str, output: str) -> None:
    f = user.get_filter(name)
    if output == 'json':
        print(json.dumps(f))
    elif output == 'table':
        print(f)


@cli.command(help='Delete a filter', aliases=['remove'])
@user_options
@click.argument('name')
@beartype
def delete(user: User, name: str) -> None:
    user.delete_filter(name)
