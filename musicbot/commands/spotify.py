import logging
import asyncio
import click
import spotify.sync as spotify
import flask
from flask import request
from prettytable import PrettyTable
from musicbot.music.spotify import spotify_user, spotify_client, spotify_id_option, spotify_secret_option, options
from musicbot import helpers

logger = logging.getLogger(__name__)
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.ERROR)


@click.group(cls=helpers.GroupWithHelp)
def cli():
    '''Spotify'''


@cli.command()
@helpers.add_options(spotify_id_option + spotify_secret_option)
def token(**kwargs):
    '''Get spotify token'''
    with spotify_client(**kwargs) as client:
        app = flask.Flask(__name__)
        app.secret_key = 'super secret key'
        REDIRECT_URI = 'http://localhost:8888/spotify/callback'
        OAUTH2_SCOPES = ('user-library-read', 'user-modify-playback-state', 'user-read-currently-playing', 'user-read-playback-state')
        oauth2 = spotify.OAuth2(client.id, REDIRECT_URI, scopes=OAUTH2_SCOPES)
        token = None

        @app.route('/spotify/callback')
        def _spotify_callback():
            try:
                code = flask.request.args['code']
            except KeyError:
                return flask.redirect('/spotify/failed')
            else:
                user = spotify.User.from_code(client, code, redirect_uri=REDIRECT_URI)
                token = user.http.bearer_info["access_token"]
                asyncio.run(user.http.close())
                print(token)
                print(user.http.refresh_token)
                shutdown_hook = request.environ.get('werkzeug.server.shutdown')
                if shutdown_hook is not None:
                    shutdown_hook()
                return flask.redirect('/')

        @app.route('/spotify/failed')
        def _spotify_failed():
            return 'Failed to authenticate with Spotify'

        @app.route('/')
        @app.route('/index')
        def _index():
            if not token:
                return flask.redirect(oauth2.url)
            return ""

        app.run('0.0.0.0', port=8888, debug=False)


def print_tracks(tracks):
    pt = PrettyTable()
    pt.field_names = ["Track", "Artists", "Album"]
    for t in tracks:
        pt.add_row([t.name, t.artist.name, t.album.name])
    print(pt)


def print_playlists(playlists):
    pt = PrettyTable()
    pt.field_names = ["Name", "Size"]
    for p in playlists:
        pt.add_row([p.name, len(p.get_all_tracks())])
    print(pt)


def print_albums(albums):
    pt = PrettyTable()
    pt.field_names = ["Name", "Artist"]
    for a in albums:
        pt.add_row([a.name, a.artist.name])
    print(pt)


def print_artists(artists):
    pt = PrettyTable()
    pt.field_names = ["Name"]
    for a in artists:
        pt.add_row([a.name])
    print(pt)


@cli.command()
@helpers.add_options(spotify_id_option + spotify_secret_option)
@click.argument("track")
def search(track, **kwargs):
    '''Search tracks'''
    with spotify_client(**kwargs) as client:
        results = client.search(track, types=['artist', 'track'])
        print_tracks(results.tracks)


@cli.command()
@helpers.add_options(options)
def playlists(**kwargs):
    '''List playlists'''
    with spotify_user(**kwargs) as user:
        playlists = user.get_all_playlists()
        print_playlists(playlists)


@cli.command()
@helpers.add_options(options)
@click.argument("name")
def playlist(name, **kwargs):
    '''Show playlist'''
    with spotify_user(**kwargs) as user:
        for p in user.get_all_playlists():
            if p.name == name:
                print_tracks(p.get_all_tracks())
                break


@cli.command()
@helpers.add_options(options)
def tracks(**kwargs):
    '''Show tracks'''
    with spotify_user(**kwargs) as user:
        tracks = user.library.get_all_tracks()
        print_tracks(tracks)


@cli.command()
@helpers.add_options(options)
def albums(**kwargs):
    '''Show albums'''
    with spotify_user(**kwargs) as user:
        albums = user.library.get_all_albums()
        print_albums(albums)
#
#
# @cli.command()
# @helpers.add_options(options)
# def artists(**kwargs):
#     '''Show artists'''
#     with spotify_user(**kwargs) as user:
#         artists = asyncio.run(user.http.followed_artists())
#         print_artists(artists)
