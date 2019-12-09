import logging
import asyncio
import click
import spotify as async_spotify
import spotify.sync as sync_spotify
import flask
from flask import request
from prettytable import PrettyTable
from musicbot import helpers
from musicbot.config import config
from musicbot.music.spotify import spotify_user, spotify_client, spotify_id_option, spotify_secret_option, options

logger = logging.getLogger(__name__)


@click.group(cls=helpers.GroupWithHelp)
def cli():
    '''Spotify'''


@cli.command()
@helpers.add_options(spotify_id_option + spotify_secret_option)
def token(**kwargs):
    '''Get spotify token'''
    with spotify_client(**kwargs) as client:
        app = flask.Flask(__name__)
        REDIRECT_URI = 'http://localhost:8888/spotify/callback'
        OAUTH2_SCOPES = ('user-library-read', 'user-follow-read', 'user-top-read', 'playlist-read-private', 'user-modify-playback-state', 'user-read-currently-playing', 'user-read-playback-state')
        oauth2 = sync_spotify.OAuth2(client.id, REDIRECT_URI, scopes=OAUTH2_SCOPES)
        token = None

        @app.route('/spotify/callback')
        def _spotify_callback():
            try:
                code = flask.request.args['code']
            except KeyError:
                return flask.redirect('/spotify/failed')
            else:
                user = sync_spotify.User.from_code(client, code, redirect_uri=REDIRECT_URI)
                token = user.http.bearer_info["access_token"]
                asyncio.run(user.http.close())
                config.configfile['DEFAULT']['spotify_token'] = token
                config.configfile['DEFAULT']['spotify_refresh_token'] = user.http.refresh_token
                with open(config.config, 'w') as output_config:
                    config.configfile.write(output_config)
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
            return "token written to config file"

        app.run('127.0.0.1', port=8888, debug=False)


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
        pt.add_row([a['name']])
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


@cli.command()
@helpers.add_options(options)
def artists(spotify_id, spotify_secret, spotify_token, spotify_refresh_token):
    '''Show artists'''
    async def get_artists():
        async with async_spotify.Client(spotify_id, spotify_secret) as client:
            user = await async_spotify.User.from_token(client, spotify_token, spotify_refresh_token)
            result = await user.http.followed_artists()
            await user.http.close()
            print_artists(result['artists']['items'])
    asyncio.run(get_artists())
