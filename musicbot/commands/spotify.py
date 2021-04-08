import logging
import operator
import textwrap
import json
import shutil
import collections
import click
from prettytable import PrettyTable, ALL  # type: ignore
from slugify import slugify
from fuzzywuzzy import fuzz  # type: ignore
from colorama import Fore  # type: ignore
from click_skeleton import AdvancedGroup, add_options

from musicbot import helpers, spotify_options, user_options
from musicbot.music import music_filter_options
from musicbot.music.file import STOPWORDS, REPLACEMENTS

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
    pt.align = 'l'
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
    pt.align = 'l'
    pt.hrules = ALL
    for distance in distances:
        st = distance['spotify_track']
        stitle = st['track']['name']
        sartist = st['track']['artists'][0]['name']
        salbum = st['track']['album']['name']
        dtitle = distance['local_track']['title']
        dartist = distance['local_track']['artist']
        dalbum = distance['local_track']['album']
        identical = True

        if stitle != dtitle:
            final_title = f"{Fore.YELLOW}{stitle} (spotify){Fore.RESET}\n{Fore.CYAN}{dtitle} (local){Fore.RESET}"
            identical = False
        else:
            final_title = f"{Fore.GREEN}{stitle}{Fore.RESET}"

        if sartist != dartist:
            final_artist = f"{Fore.YELLOW}{sartist} (spotify){Fore.RESET}\n{Fore.CYAN}{dartist} (local){Fore.RESET}"
            identical = False
        else:
            final_artist = f"{Fore.GREEN}{sartist}{Fore.RESET}"

        if salbum != dalbum:
            final_album = f"{Fore.YELLOW}{salbum} (spotify){Fore.RESET}\n{Fore.CYAN}{dalbum} (local){Fore.RESET}"
            identical = False
        else:
            final_album = f"{Fore.GREEN}{salbum}{Fore.RESET}"

        if identical:
            continue

        d = distance['distance']
        pt.add_row([
            final_title,
            final_artist,
            final_album,
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


@click.group('spotify', help='Spotify tool', cls=AdvancedGroup)
def cli():
    pass


@cli.command(help='Token informations')
@add_options(spotify_options.options)
def cached_token(spotify):
    print(spotify.cached_token())
    print(f"Expired : {spotify.is_token_expired()}")


@cli.command(help='Get a new token')
@add_options(spotify_options.options)
def refresh_token(spotify):
    print(spotify.refresh_token())


@cli.command(help='List playlists')
@add_options(spotify_options.options)
def playlists(spotify):
    print_playlists_table(spotify.playlists())


@cli.command(help='Show playlist')
@add_options(
    spotify_options.options,
    helpers.output_option,
)
@click.argument("name")
def playlist(name, spotify, output):
    tracks = spotify.playlist_tracks(name)
    output_tracks(output, tracks)


@cli.command(help='Show tracks')
@add_options(
    spotify_options.options,
    helpers.output_option,
)
def tracks(spotify, output):
    tracks = spotify.tracks()
    output_tracks(output, tracks)


@cli.command(help='Diff between local and spotify')
@add_options(
    user_options.options,
    spotify_options.options,
    music_filter_options.options,
    helpers.output_option,
)
@click.option('--download-playlist', help='Create the download playlist', is_flag=True)
@click.option('--min-threshold', help='Minimum distance threshold', type=click.FloatRange(0, 100), default=90)
@click.option('--max-threshold', help='Maximum distance threshold', type=click.FloatRange(0, 100), default=100)
def diff(user, download_playlist, music_filter, spotify, output, min_threshold, max_threshold):
    spotify_tracks = spotify.tracks()
    spotify_tracks_by_slug = {
        # slugify(f"""{t['track']['artists'][0]['name']}-{t['track']['album']['name']}-{t['track']['name']}""", stopwords=STOPWORDS, replacements=REPLACEMENTS):  # type: ignore
        slugify(f"""{t['track']['artists'][0]['name']}-{t['track']['name']}""", stopwords=STOPWORDS, replacements=REPLACEMENTS):  # type: ignore
        t for t in spotify_tracks
    }

    local_tracks = user.do_filter(music_filter)
    local_tracks_by_slug = {
        # slugify(f"""{t['artist']}-{t['album']}-{t['title']}""", stopwords=STOPWORDS, replacements=REPLACEMENTS):  # type: ignore
        slugify(f"""{t['artist']}-{t['title']}""", stopwords=STOPWORDS, replacements=REPLACEMENTS):  # type: ignore
        t for t in local_tracks
    }

    spotify_differences = set(spotify_tracks_by_slug.keys()).difference(set(local_tracks_by_slug.keys()))
    spotify_slug_tracks = collections.OrderedDict((d, spotify_tracks_by_slug[d]) for d in sorted(spotify_differences))

    local_tracks_found = len(spotify_tracks_by_slug) - len(spotify_differences)
    if len(local_tracks) == local_tracks_found:
        return

    if download_playlist:
        spotify.set_download_playlist(spotify_slug_tracks.values())

    output_tracks(output, spotify_slug_tracks.values())
    distances_tracks = []
    for spotify_slug, spotify_track in spotify_slug_tracks.items():
        distances = {
            local_slug: fuzz.ratio(spotify_slug, local_slug)
            for local_slug in local_tracks_by_slug
        }
        if not distances:
            continue
        closest_local_track = max(distances.items(), key=operator.itemgetter(1))
        closest_local_slug = closest_local_track[0]
        closest_distance = closest_local_track[1]

        if min_threshold <= closest_distance <= max_threshold:
            if 'spotify-error' in local_tracks_by_slug[closest_local_slug]['keywords']:
                continue
            distances_tracks.append({
                'local_track': local_tracks_by_slug[closest_local_slug],
                'local_slug': closest_local_slug,
                'spotify_track': spotify_track,
                'spotify_slug': spotify_slug,
                'distance': closest_distance,
            })
    print_distances(distances_tracks)
    print(f"spotify tracks : {len(spotify_tracks)}")
    print(f"spotify slugs: {len(spotify_tracks_by_slug)}")
    print(f"local tracks : {len(local_tracks)}")
    print(f"local tracks slugs : {len(local_tracks_by_slug)}")
    print(f"found in local     : {local_tracks_found}")
    print(f"not found in local : {len(spotify_differences)}")
