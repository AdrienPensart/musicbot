import logging
import json
import click
from slugify import slugify
from musicbot import helpers

logger = logging.getLogger(__name__)


@click.group(help='JSON tools for music libraries', cls=helpers.GroupWithHelp)
def cli():
    pass


@cli.command(help='Diff tracks')
@click.argument('source', type=click.File('r'))
@click.argument('destination', type=click.File('r'))
def diff(source, destination):
    source = json.loads(source.read())
    destination = json.loads(destination.read())
    stopwords = ['the', 'remaster', 'remastered', 'cut', 'part'] + list(map(str, range(1900, 2020)))
    replacements = [['praxis', 'buckethead'], ['lawson-rollins', 'buckethead']]
    source_items = {slugify(f"""{t['artist']}-{t['title']}""", stopwords=stopwords, replacements=replacements) for t in source}
    destination_items = {slugify(f"""{t['artist']}-{t['title']}""", stopwords=stopwords, replacements=replacements) for t in destination}
    differences = source_items.difference(destination_items)
    differences = sorted(differences)
    for difference in differences:
        print(difference)
    print(f"diff : {len(differences)}")
