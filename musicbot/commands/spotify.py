import logging
import operator
import textwrap
import json
import shutil
import collections
import click
import jellyfish  # type: ignore
from prettytable import PrettyTable  # type: ignore
from slugify import slugify  # type: ignore
from colorama import Fore  # type: ignore
from click_skeleton import AdvancedGroup, add_options

from musicbot import helpers
from musicbot.spotify import spotify_options
from musicbot.user import auth_options

logger = logging.getLogger(__name__)


def dump_tracks(tracks):
    tracks = [
        {
            'title': t['track']['name'],
            'artist': t['track']['artists'][0]['name'],
            'album': t['track']['album']['name'],
        } for t in tracks
    ]
    print(json.dumps(tracks))


def print_tracks_table(tracks):
    if not tracks:
        return
    pt = PrettyTable(["Track", "Artist", "Album"])
    width = shutil.get_terminal_size().columns // 3
    for t in tracks:
        title = '\n'.join(textwrap.wrap(t['track']['name'], width))
        artist = '\n'.join(textwrap.wrap(t['track']['artists'][0]['name'], width))
        album = '\n'.join(textwrap.wrap(t['track']['album']['name'], width))
        pt.add_row([title, artist, album])
    print(pt)


def print_distances(distances):
    if not distances:
        return
    pt = PrettyTable(["Title", "Artist", "Album", "Distance"])
    for distance in distances:
        st = distance['spotify_track']
        stitle = st['track']['name']
        sartist = st['track']['artists'][0]['name']
        salbum = st['track']['album']['name']
        lt = distance['local_track']
        d = distance['distance']
        pt.add_row([
            f"{Fore.GREEN}Spotify : {stitle}{Fore.RESET}\nLocal : {lt['title']}",
            f"{Fore.GREEN}Spotify : {sartist}{Fore.RESET}\n Local : {lt['artist']}",
            f"{Fore.GREEN}Spotify : {salbum}{Fore.RESET}\nLocal : {lt['album']}",
            d,
        ])
    print(pt)


def print_playlists_table(playlists):
    if not playlists:
        return
    pt = PrettyTable(["Name", "Size"])
    for p in playlists:
        pt.add_row([p['name'], p['tracks']['total']])
    print(pt.get_string(title='Spotify playlists'))


def output_tracks(output: str, tracks):
    if output == 'table':
        print_tracks_table(tracks)
    elif output == 'json':
        dump_tracks(tracks)


@click.group(help='Spotify tool', cls=AdvancedGroup)
def cli():
    pass


@cli.command(help='List playlists')
@add_options(spotify_options)
def playlists(spotify):
    print_playlists_table(spotify.playlists())


@cli.command(help='Show playlist')
@add_options(
    spotify_options +
    helpers.output_option
)
@click.argument("name")
def playlist(name, spotify, output):
    tracks = spotify.playlist(name)
    output_tracks(output, tracks)


@cli.command(help='Show tracks')
@add_options(
    spotify_options +
    helpers.output_option
)
def tracks(spotify, output):
    tracks = spotify.tracks()
    output_tracks(output, tracks)


@cli.command(help='Diff between local and spotify')
@add_options(
    auth_options +
    spotify_options +
    helpers.output_option
)
@click.option('--min-threshold', help='Minimum distance threshold', type=click.FloatRange(0.0, 1.0), default=0.9)
@click.option('--max-threshold', help='Maximum distance threshold', type=click.FloatRange(0.0, 1.0), default=1.0)
def diff(user, spotify, output, min_threshold, max_threshold):
    stopwords = ['the', 'remaster', 'remastered', 'cut', 'part', 'version', 'mix', 'deluxe', 'edit', 'album', 'lp'] + list(map(str, range(1900, 2020)))
    replacements = [['praxis', 'buckethead'], ['lawson-rollins', 'buckethead']]

    spotify_tracks = spotify.tracks()
    local_tracks = user.do_filter()

    spotify_tracks = {
        slugify(f"""{t['track']['artists'][0]['name']}-{t['track']['name']}""", stopwords=stopwords, replacements=replacements):
        t for t in spotify_tracks
    }

    local_tracks = {
        slugify(f"""{t['artist']}-{t['title']}""", stopwords=stopwords, replacements=replacements):
        t for t in local_tracks
    }

    spotify_differences = set(spotify_tracks.keys()).difference(set(local_tracks.keys()))
    spotify_slug_tracks = collections.OrderedDict((d, spotify_tracks[d]) for d in sorted(spotify_differences))

    output_tracks(output, spotify_slug_tracks.values())
    print(f"found in local     : {len(local_tracks) - len(spotify_differences)}")
    print(f"not found in local : {len(spotify_differences)}")

    distances_tracks = []
    for spotify_slug, spotify_track in spotify_slug_tracks.items():
        distances = {
            local_slug: jellyfish.jaro_distance(spotify_slug, local_slug)
            for local_slug in local_tracks
        }
        closest_local_track = max(distances.items(), key=operator.itemgetter(1))
        closest_local_slug = closest_local_track[0]
        closest_distance = closest_local_track[1]

        if min_threshold <= closest_distance <= max_threshold:
            if 'spotify-error' in local_tracks[closest_local_slug]['keywords']:
                continue
            distances_tracks.append({
                'local_track': local_tracks[closest_local_slug],
                'local_slug': closest_local_slug,
                'spotify_track': spotify_track,
                'spotify_slug': spotify_slug,
                'distance': closest_distance,
            })
    print_distances(distances_tracks)
