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
from click_skeleton import AdvancedGroup
from musicbot.cli.options import output_option
from musicbot.cli.spotify import spotify_options
from musicbot.cli.user import user_options
from musicbot.cli.music_filter import music_filter_options
from musicbot.music.file import STOPWORDS, REPLACEMENTS
from musicbot.music.music_filter import MusicFilter
from musicbot.spotify import Spotify
from musicbot.user import User

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

        colored_stitle = click.style(f"{stitle} (spotify)", fg='yellow')
        if stitle != dtitle:
            colored_dtitle = click.style(f"{dtitle} (local)", fg="cyan")
            final_title = f"{colored_stitle}\n{colored_dtitle}"
            identical = False
        else:
            final_title = colored_stitle

        colored_sartist = click.style(f"{sartist} (spotify)", fg='yellow')
        if sartist != dartist:
            colored_dartist = click.style(f"{dartist} (local)", fg="cyan")
            final_artist = f"{colored_stitle}\n{colored_dartist}"
            identical = False
        else:
            final_artist = colored_sartist

        colored_salbum = click.style(f"{salbum} (spotify)", fg='yellow')
        if salbum != dalbum:
            colored_dalbum = click.style(f"{dalbum} (local)", fg="cyan")
            final_album = f"{colored_salbum}\n{colored_dalbum}"
            identical = False
        else:
            final_album = colored_salbum

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


@cli.command(help='Generate a new token', aliases=['auth'])
@spotify_options
def new_token(spotify: Spotify):
    print(spotify.new_token())


@cli.command(help='Token informations')
@spotify_options
def cached_token(spotify: Spotify):
    print(spotify.cached_token())
    print(f"Expired : {spotify.is_token_expired()}")


@cli.command(help='Get a new token')
@spotify_options
def refresh_token(spotify: Spotify):
    print(spotify.refresh_token())


@cli.command(help='List playlists')
@spotify_options
def playlists(spotify: Spotify):
    print_playlists_table(spotify.playlists())


@cli.command(help='Show playlist')
@spotify_options
@output_option
@click.argument("name")
def playlist(name: str, spotify: Spotify, output: str):
    tracks = spotify.playlist_tracks(name)
    output_tracks(output, tracks)


@cli.command(help='Show tracks')
@spotify_options
@output_option
def tracks(spotify: Spotify, output: str):
    tracks = spotify.tracks()
    output_tracks(output, tracks)


@cli.command(help='Diff between local and spotify')
@user_options
@spotify_options
@music_filter_options
@output_option
@click.option('--download-playlist', help='Create the download playlist', is_flag=True)
@click.option('--min-threshold', help='Minimum distance threshold', type=click.FloatRange(0, 100), default=90)
@click.option('--max-threshold', help='Maximum distance threshold', type=click.FloatRange(0, 100), default=100)
def diff(user: User, download_playlist: bool, music_filter: MusicFilter, spotify: Spotify, output: str, min_threshold: float, max_threshold: float):
    spotify_tracks = spotify.tracks()
    spotify_tracks_by_slug = {
        # slugify(f"""{t['track']['artists'][0]['name']}-{t['track']['album']['name']}-{t['track']['name']}""", stopwords=STOPWORDS, replacements=REPLACEMENTS):
        slugify(f"""{t['track']['artists'][0]['name']}-{t['track']['name']}""", stopwords=STOPWORDS, replacements=REPLACEMENTS):
        t for t in spotify_tracks
    }

    local_tracks = user.playlist(music_filter)
    local_tracks_by_slug = {
        # slugify(f"""{t['artist']}-{t['album']}-{t['title']}""", stopwords=STOPWORDS, replacements=REPLACEMENTS):
        slugify(f"""{t['artist']}-{t['title']}""", stopwords=STOPWORDS, replacements=REPLACEMENTS):
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
