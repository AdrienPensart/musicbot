import click
from musicbot import helpers
from musicbot.music.file import File
from musicbot.music.fingerprint import acoustid_apikey_option


@click.group(cls=helpers.GroupWithHelp)
def cli():
    '''Fingerprint tool'''


@cli.command()
@click.argument('path')
@helpers.add_options(acoustid_apikey_option)
def search(path, acoustid_apikey):
    '''Find music with fingerprint'''
    f = File(path)
    print(f.fingerprint(acoustid_apikey))
