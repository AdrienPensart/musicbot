import click
from musicbot import helpers
from musicbot.music import youtube


@click.group(cls=helpers.GroupWithHelp)
def cli():
    '''Youtube tool'''


@cli.command()
@click.argument('artist')
@click.argument('title')
def search(artist, title):
    '''Generate some stats for music collection with filters'''
    print(youtube.search(artist, title))
