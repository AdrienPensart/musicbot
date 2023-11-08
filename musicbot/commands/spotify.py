import logging
import operator

import click
from beartype import beartype
from click_skeleton import AdvancedGroup
from click_skeleton.helpers import PrettyDefaultDict
from fuzzywuzzy import fuzz  # type: ignore
from slugify import slugify

from musicbot import (
    MusicDb,
    MusicbotObject,
    Spotify,
    syncify,
)
from musicbot.cli.musicdb import musicdb_options
from musicbot.cli.options import dry_option, output_option
from musicbot.cli.spotify import (
    output_tracks,
    print_distances,
    print_playlists_table,
    spotify_options,
)
from musicbot.defaults import DEFAULT_SPOTIFY_DOWNLOAD_PLAYLIST, REPLACEMENTS, STOPWORDS

logger = logging.getLogger(__name__)


@click.group("spotify", help="Spotify tool", cls=AdvancedGroup)
@beartype
def cli() -> None:
    pass


@cli.command(help="Generate a new token", aliases=["login", "auth"])
@spotify_options
@dry_option
@beartype
def new_token(spotify: Spotify) -> None:
    print(spotify.new_token())


@cli.command(help="Token informations")
@spotify_options
@dry_option
@beartype
def cached_token(spotify: Spotify) -> None:
    token = spotify.cached_token()
    MusicbotObject.print_json(token)
    MusicbotObject.success(f"Expired : {spotify.is_token_expired(token)}")


@cli.command(help="Get a new token")
@spotify_options
@dry_option
@beartype
def refresh_token(spotify: Spotify) -> None:
    print(spotify.refresh_token())


@cli.command(help="List playlists")
@spotify_options
@beartype
def playlists(spotify: Spotify) -> None:
    if (playlists := spotify.playlists()) is None:
        return
    print_playlists_table(playlists)


@cli.command(help="Show playlist")
@spotify_options
@output_option
@click.argument("name")
@beartype
def playlist(name: str, spotify: Spotify, output: str) -> None:
    if (tracks := spotify.playlist_tracks(name)) is None:
        return
    output_tracks(output, tracks)


@cli.command(help="Show download playlist")
@spotify_options
@output_option
@beartype
def to_download(spotify: Spotify, output: str) -> None:
    if (tracks := spotify.playlist_tracks(DEFAULT_SPOTIFY_DOWNLOAD_PLAYLIST)) is None:
        return
    output_tracks(output, tracks)


@cli.command(help="Show liked tracks", aliases=["liked"])
@spotify_options
@output_option
@beartype
def tracks(spotify: Spotify, output: str) -> None:
    if (tracks := spotify.liked_tracks()) is None:
        return
    output_tracks(output, tracks)


@cli.command(help="Artists diff between local and spotify")
@spotify_options
@musicdb_options
@syncify
@beartype
async def artist_diff(musicdb: MusicDb, spotify: Spotify) -> None:
    if (spotify_tracks := spotify.liked_tracks()) is None:
        return
    spotify_tracks_by_artist = PrettyDefaultDict(list)
    for spotify_track in spotify_tracks:
        spotify_artist_slug = slugify(spotify_track["track"]["artists"][0]["name"])
        spotify_tracks_by_artist[spotify_artist_slug].append(spotify_track["track"])

    local_playlist = await musicdb.make_playlist()
    local_tracks_by_artist = PrettyDefaultDict(list)
    for local_track in local_playlist.musics:
        local_artist_slug = slugify(local_track.artist)
        local_tracks_by_artist[local_artist_slug].append(local_track)

    spotify_differences = set(spotify_tracks_by_artist.keys()).difference(set(local_tracks_by_artist.keys()))
    for spotify_difference in sorted(spotify_differences):
        print(spotify_difference)

    MusicbotObject.success(f"spotify artists : {len(spotify_tracks_by_artist)}")
    MusicbotObject.success(f"local artists : {len(local_tracks_by_artist)}")


@cli.command(help="Diff between local and spotify")
@spotify_options
@musicdb_options
@output_option
@click.option("--download-playlist", help="Create the download playlist", is_flag=True)
@click.option("--min-threshold", help="Minimum distance threshold", type=click.FloatRange(0, 100), default=90, show_default=True)
@click.option("--max-threshold", help="Maximum distance threshold", type=click.FloatRange(0, 100), default=100, show_default=True)
@syncify
@beartype
async def track_diff(musicdb: MusicDb, download_playlist: bool, spotify: Spotify, output: str, min_threshold: float, max_threshold: float) -> None:
    if (spotify_tracks := spotify.liked_tracks()) is None:
        return
    spotify_tracks_by_slug = {slugify(f"""{t['track']['artists'][0]['name']}-{t['track']['name']}""", stopwords=STOPWORDS, replacements=REPLACEMENTS): t for t in spotify_tracks}

    local = await musicdb.make_playlist()
    local_music_by_slug = {music.slug: music for music in local.musics}

    spotify_differences = set(spotify_tracks_by_slug.keys()).difference(set(local_music_by_slug.keys()))
    spotify_slug_tracks = dict((d, spotify_tracks_by_slug[d]) for d in sorted(spotify_differences))

    local_tracks_found = len(spotify_tracks_by_slug) - len(spotify_differences)
    # if len(local.musics) == local_tracks_found:
    #     return

    if download_playlist:
        spotify.set_download_playlist(spotify_slug_tracks.values())

    output_tracks(output, list(spotify_slug_tracks.values()))
    distances_tracks = []
    for spotify_slug, spotify_track in spotify_slug_tracks.items():
        distances = {local_slug: fuzz.ratio(spotify_slug, local_slug) for local_slug in local_music_by_slug}
        if not distances:
            continue
        closest_local_track = max(distances.items(), key=operator.itemgetter(1))
        closest_local_slug = closest_local_track[0]
        closest_distance = closest_local_track[1]

        if min_threshold <= closest_distance <= max_threshold:
            if "spotify-error" in local_music_by_slug[closest_local_slug].keywords:
                continue
            distances_tracks.append(
                {
                    "local_track": local_music_by_slug[closest_local_slug],
                    "local_slug": closest_local_slug,
                    "spotify_track": spotify_track,
                    "spotify_slug": spotify_slug,
                    "distance": closest_distance,
                }
            )
    print_distances(distances_tracks)
    MusicbotObject.success(f"spotify tracks : {len(spotify_tracks)}")
    MusicbotObject.success(f"spotify slugs: {len(spotify_tracks_by_slug)}")
    MusicbotObject.success(f"local tracks : {len(local.musics)}")
    MusicbotObject.success(f"local tracks slugs : {len(local_music_by_slug)}")
    MusicbotObject.success(f"found in local     : {local_tracks_found}")
    MusicbotObject.success(f"not found in local : {len(spotify_differences)}")
