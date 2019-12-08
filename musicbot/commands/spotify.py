import logging
import asyncio
from contextlib import contextmanager
import click
import spotify.sync as spotify
import flask
from flask import request
from musicbot.music.spotify import spotify_id_option, spotify_secret_option, options
from musicbot import helpers

logger = logging.getLogger(__name__)
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.ERROR)


@click.group(cls=helpers.GroupWithHelp)
def cli():
    '''Spotify'''


@cli.command()
@helpers.add_options(spotify_id_option + spotify_secret_option)
def token(spotify_id, spotify_secret):
    '''Get spotify token'''
    client = spotify.Client(spotify_id, spotify_secret)
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

    app.run('127.0.0.1', port=8888, debug=False)
    client.close()


@contextmanager
def spotify_client(spotify_id, spotify_secret):
    try:
        client = spotify.Client(spotify_id, spotify_secret)
        yield client
    finally:
        client.close()


@contextmanager
def spotify_user(spotify_token, **kwargs):
    try:
        with spotify_client(**kwargs) as client:
            user = spotify.User.from_token(client, spotify_token)
            yield user
    finally:
        asyncio.run(user.http.close())


@cli.command()
@helpers.add_options(spotify_id_option + spotify_secret_option)
@click.argument("track")
def search(track, **kwargs):
    '''Search tracks'''
    with spotify_client(**kwargs) as client:
        results = client.search(track, types=['artist', 'track'])
        print(results.tracks)


@cli.command()
@helpers.add_options(options)
def playlists(**kwargs):
    '''Show playlists'''
    with spotify_user(**kwargs) as user:
        playlists = user.get_all_playlists()
        print(playlists)


@cli.command()
@helpers.add_options(options)
def tracks(**kwargs):
    '''Show tracks'''
    with spotify_user(**kwargs) as user:
        tracks = user.library.get_all_tracks()
        print(tracks)


@cli.command()
@helpers.add_options(options)
def albums(**kwargs):
    '''Show albums'''
    with spotify_user(**kwargs) as user:
        albums = user.library.get_all_albums()
        print(albums)
