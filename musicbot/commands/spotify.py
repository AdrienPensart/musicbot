import logging
import json
import click
from prettytable import PrettyTable
from musicbot import helpers
from musicbot.music.spotify import get_search, get_tracks, get_playlists, get_playlist, spotify_token_option

logger = logging.getLogger(__name__)


@click.group(cls=helpers.GroupWithHelp)
def cli():
    '''Spotify tool'''


def print_tracks(tracks):
    pt = PrettyTable()
    pt.field_names = ["Track", "Artist", "Album"]
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
@click.argument('query')
def search(**kwargs):
    get_search(**kwargs)


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
@helpers.add_options(spotify_token_option + helpers.output_option)
def tracks(spotify_token, output):
    '''Show tracks'''
    tracks = get_tracks(spotify_token)
    if output == 'table':
        print_tracks(tracks)
    elif output == 'json':
        tracks_dict = [{'title': t['track']['name'], 'artist': t['track']['artists'][0]['name'], 'album': t['track']['album']['name']} for t in tracks]
        print(json.dumps(tracks_dict))
