import logging
import click
from musicbot import helpers
from musicbot.music.file import File
from musicbot.music.fingerprint import acoustid_apikey_option

logger = logging.getLogger(__name__)


@click.group(help='''Music file''', cls=helpers.GroupWithHelp)
def cli():
    pass


@cli.command(help='''Print music fingerprint''')
@click.argument('path')
@helpers.add_options(acoustid_apikey_option)
def fingerprint(path, acoustid_apikey):
    f = File(path)
    print(f.fingerprint(acoustid_apikey))
