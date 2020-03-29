import logging
import click
from prettytable import PrettyTable
from musicbot import helpers
from musicbot.music.spotify import get_tracks, get_playlists, get_playlist, spotify_token_option

logger = logging.getLogger(__name__)


@click.group(cls=helpers.GroupWithHelp)
def cli():
    '''Spotify'''


def print_tracks(tracks):
    pt = PrettyTable()
    pt.field_names = ["Track", "Artists", "Album"]
    for t in tracks:
        pt.add_row([t['track']['name'], t['track']['artists'][0]['name'], t['track']['album']['name']])
    print(pt)


def print_playlists(playlists):
    pt = PrettyTable()
    pt.field_names = ["Name", "Size"]
    for p in playlists:
        pt.add_row([p['name'], p['tracks']['total']])
    print(pt)


@cli.command()
@helpers.add_options(spotify_token_option)
def playlists(spotify_token):
    '''List playlists'''
    playlists = get_playlists(spotify_token)
    print_playlists(playlists)


@cli.command()
@helpers.add_options(spotify_token_option)
@click.argument("name")
def playlist(name, spotify_token):
    '''Show playlist'''
    tracks = get_playlist(name, spotify_token)
    print_tracks(tracks)


@cli.command()
@helpers.add_options(spotify_token_option)
def tracks(spotify_token):
    '''Show tracks'''
    tracks = get_tracks(spotify_token)
    print_tracks(tracks)
