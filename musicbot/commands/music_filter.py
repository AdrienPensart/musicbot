import logging
import json
import click
from click_skeleton import AdvancedGroup, add_options
from prettytable import PrettyTable  # type: ignore
from musicbot import helpers, user_options

logger = logging.getLogger(__name__)


@click.group('filter', help='Filter management', cls=AdvancedGroup)
def cli():
    pass


@cli.command(help='Load default filters')
@add_options(user_options.auth_options)
def load(user):
    user.load_default_filters()


@cli.command(help='Count filters')
@add_options(user_options.auth_options)
def count(user):
    print(user.count_filters())


@cli.command('list', help='List filters')
@add_options(
    helpers.output_option,
    user_options.auth_options,
)
def _list(user, output):
    if output == 'json':
        print(json.dumps(user.list_filters()))
    elif output == 'table':
        pt = PrettyTable()
        pt.field_names = ["Name", "Keywords", "No keywords", "Min rating", "Max rating"]
        for f in user.list_filters():
            pt.add_row([f['name'], f['keywords'], f['noKeywords'], f['minRating'], f['maxRating']])
        print(pt)


@cli.command(help='Print a filter', aliases=['get', 'print'])
@add_options(
    helpers.output_option,
    user_options.auth_options,
)
@click.argument('name')
def show(user, name, output):
    f = user.get_filter(name)
    if output == 'json':
        print(json.dumps(f))
    elif output == 'table':
        print(f)


@cli.command(help='Delete a filter', aliases=['remove'])
@add_options(
    user_options.auth_options,
)
@click.argument('name')
def delete(user, name):
    user.delete_filter(name)
