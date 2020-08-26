import logging
import json
import click
from slugify import slugify
from click_skeleton import AdvancedGroup, add_options

from musicbot import helpers
from musicbot.spotify import spotify_options
from musicbot.user import auth_options

logger = logging.getLogger(__name__)


@click.group(help='Spotify tool', cls=AdvancedGroup)
def cli():
    pass


@cli.command(help='List playlists')
@add_options(spotify_options)
def playlists(spotify):
    spotify.print_playlists()


@cli.command(help='Show playlist')
@add_options(spotify_options)
@click.argument("name")
def playlist(name, spotify):
    spotify.print_tracks(name)


@cli.command(help='Show tracks')
@add_options(
    spotify_options +
    helpers.output_option
)
def tracks(spotify, output):
    if output == 'table':
        spotify.print_tracks()
    elif output == 'json':
        spotify_tracks = spotify.tracks()
        spotify_tracks = [
            {
                'title': t['track']['name'],
                'artist': t['track']['artists'][0]['name'],
                'album': t['track']['album']['name']
            } for t in spotify_tracks
        ]
        print(json.dumps(spotify_tracks))


@cli.command(help='Diff between local and spotify')
@add_options(auth_options + spotify_options)
def diff(user, spotify):
    spotify_tracks = spotify.tracks()
    spotify_tracks = [
        {
            'title': t['track']['name'],
            'artist': t['track']['artists'][0]['name'],
            'album': t['track']['album']['name']
        } for t in spotify_tracks
    ]
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
