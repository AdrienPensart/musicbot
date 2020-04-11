import logging
import json
import click
from slugify import slugify
from prettytable import PrettyTable
from musicbot import helpers
from musicbot.music.spotify import spotify_options
from musicbot.user import auth_options

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
@helpers.add_options(spotify_options)
def playlists(spotify):
    '''List playlists'''
    playlists = spotify.playlists()
    print_playlists(playlists)


@cli.command()
@helpers.add_options(spotify_options)
@click.argument("name")
def playlist(name, spotify):
    '''Show playlist'''
    tracks = spotify.playlist(name)
    print_tracks(tracks)


@cli.command()
@helpers.add_options(spotify_options + helpers.output_option)
def tracks(spotify, output):
    '''Show tracks'''
    spotify_tracks = spotify.tracks()
    if output == 'table':
        print_tracks(tracks)
    elif output == 'json':
        spotify_tracks = [{'title': t['track']['name'], 'artist': t['track']['artists'][0]['name'], 'album': t['track']['album']['name']} for t in spotify_tracks]
        print(json.dumps(spotify_tracks))


@cli.command(help='Diff between local and spotify')
@helpers.add_options(auth_options + spotify_options + helpers.output_option)
def diff(user, spotify, output):
    spotify_tracks = spotify.tracks()
    spotify_tracks = [{'title': t['track']['name'], 'artist': t['track']['artists'][0]['name'], 'album': t['track']['album']['name']} for t in spotify_tracks]
    local_tracks = user.do_filter()

    stopwords = ['the', 'remaster', 'remastered', 'cut', 'part'] + list(map(str, range(1900, 2020)))
    replacements = [['praxis', 'buckethead'], ['lawson-rollins', 'buckethead']]
    source_items = {slugify(f"""{t['artist']}-{t['title']}""", stopwords=stopwords, replacements=replacements) for t in spotify_tracks}
    destination_items = {slugify(f"""{t['artist']}-{t['title']}""", stopwords=stopwords, replacements=replacements) for t in local_tracks}
    differences = source_items.difference(destination_items)

    differences = sorted(differences)
    for difference in differences:
        print(difference)
    print(f"diff : {len(differences)}")
