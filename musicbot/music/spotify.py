import logging
import itertools
from functools import partial
import spotipy
import click
from musicbot.helpers import config_string

logger = logging.getLogger(__name__)

MB_SPOTIFY_ID = 'MB_SPOTIFY_ID'
spotify_id_option = [click.option('--spotify-id', help='Spotify ID', callback=partial(config_string, MB_SPOTIFY_ID, 'spotify_id', True))]

MB_SPOTIFY_SECRET = 'MB_SPOTIFY_SECRET'
spotify_secret_option = [click.option('--spotify-secret', help='Spotify secret', callback=partial(config_string, MB_SPOTIFY_SECRET, 'spotify_secret', True))]

MB_SPOTIFY_TOKEN = 'MB_SPOTIFY_TOKEN'
spotify_token_option = [click.option('--spotify-token', help='Spotify token', callback=partial(config_string, MB_SPOTIFY_TOKEN, 'spotify_token', True))]

# MB_SPOTIFY_REFRESH_TOKEN = 'MB_SPOTIFY_REFRESH_TOKEN'
# spotify_refresh_token_option = [click.option('--spotify-refresh-token', help='Spotify refresh token', callback=partial(config_string, MB_SPOTIFY_REFRESH_TOKEN, 'spotify_refresh_token', False))]

options = spotify_id_option + spotify_secret_option + spotify_token_option  # + spotify_refresh_token_option


def get_search(spotify_token, query):
    sp = spotipy.Spotify(auth=spotify_token)
    results = sp.search(q=query, type='artist')
    print(results.keys())
    print(results["artists"])
    # items = results['tracks']['items']
    # if len(items) > 0:
    #     track = items[0]
    #     print(track['name'])


def get_tracks(spotify_token):
    sp = spotipy.Spotify(auth=spotify_token)
    offset = 0
    limit = 50
    objects = []
    while True:
        new_objects = sp.current_user_saved_tracks(limit=limit, offset=offset)
        objects.append(new_objects['items'])
        logger.info("chunk size: %s", len(new_objects['items']))
        offset += len(new_objects['items'])
        if len(new_objects['items']) < limit:
            break
    return list(itertools.chain(*objects))


def get_playlists(spotify_token):
    sp = spotipy.Spotify(auth=spotify_token)
    offset = 0
    limit = 50
    objects = []
    while True:
        new_objects = sp.current_user_playlists(limit=limit, offset=offset)
        length = len(new_objects['items'])
        objects.append(new_objects['items'])
        logger.info("chunk size: %s", length)
        offset += length
        if length < limit:
            break
    logger.debug("length: %s", offset)
    return list(itertools.chain(*objects))


def get_playlist(name, spotify_token):
    sp = spotipy.Spotify(auth=spotify_token)
    playlists = get_playlists(spotify_token)
    for p in playlists:
        if p['name'] == name:
            tracks = []
            results = sp.playlist(p['id'], fields="tracks,next")
            new_tracks = results['tracks']
            tracks.append(new_tracks['items'])
            while new_tracks['next']:
                new_tracks = sp.next(new_tracks)
                tracks.append(new_tracks['tracks']['items'])
            return list(itertools.chain(*tracks))
    return []
