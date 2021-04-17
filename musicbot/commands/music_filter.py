import logging
import json
import click
from click_skeleton import AdvancedGroup
from prettytable import PrettyTable  # type: ignore
from musicbot.cli.options import output_option
from musicbot.cli.user import user_options

logger = logging.getLogger(__name__)


@click.group('filter', help='Filter management', cls=AdvancedGroup)
def cli():
    pass


@cli.command(help='Load default filters')
@user_options
def load(user):
    user.load_default_filters()


@cli.command(help='Count filters')
@user_options
def count(user):
    print(user.count_filters())


@cli.command('list', help='List filters')
@output_option
@user_options
def _list(user, output):
    if output == 'json':
        print(json.dumps(user.list_filters()))
    elif output == 'table':
        pt = PrettyTable(["Name", "Keywords", "No keywords", "Min rating", "Max rating"])
        for f in user.list_filters():
            pt.add_row([f['name'], f['keywords'], f['noKeywords'], f['minRating'], f['maxRating']])
        print(pt)


@cli.command(help='Print a filter', aliases=['get', 'print'])
@output_option
@user_options
@click.argument('name')
def show(user, name, output):
    f = user.get_filter(name)
    if output == 'json':
        print(json.dumps(f))
    elif output == 'table':
        print(f)


@cli.command(help='Delete a filter', aliases=['remove'])
@user_options
@click.argument('name')
def delete(user, name):
    user.delete_filter(name)
