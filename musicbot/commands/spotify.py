import logging
import json
import click
from prettytable import PrettyTable
from musicbot import helpers
from musicbot.music.spotify import spotify_token_option

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
def playlists(spotify):
    '''List playlists'''
    playlists = spotify.playlists()
    print_playlists(playlists)


@cli.command()
@helpers.add_options(spotify_token_option)
@click.argument("name")
def playlist(name, spotify):
    '''Show playlist'''
    tracks = spotify.playlist(name)
    print_tracks(tracks)


@cli.command()
@helpers.add_options(spotify_token_option + helpers.output_option)
def tracks(spotify, output):
    '''Show tracks'''
    tracks = spotify.tracks()
    if output == 'table':
        print_tracks(tracks)
    elif output == 'json':
        tracks_dict = [{'title': t['track']['name'], 'artist': t['track']['artists'][0]['name'], 'album': t['track']['album']['name']} for t in tracks]
        print(json.dumps(tracks_dict))
