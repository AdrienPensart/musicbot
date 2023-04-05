import asyncio
import codecs
import io
import logging
import shutil
import webbrowser
from pathlib import Path
from typing import Any

import click
import progressbar  # type: ignore
from attr import asdict
from beartype import beartype
from click_skeleton import AdvancedGroup
from rich.table import Table
from watchfiles import Change, DefaultFilter, awatch

from musicbot.cli.file import flat_option
from musicbot.cli.folder import destination_argument, folder_argument, folders_argument
from musicbot.cli.music_filter import filters_reprs, music_filters_options
from musicbot.cli.musicdb import musicdb_options
from musicbot.cli.options import (
    clean_option,
    dry_option,
    lazy_yes_option,
    output_option,
    save_option,
    yes_option,
)
from musicbot.cli.playlist import bests_options, playlist_options
from musicbot.defaults import DEFAULT_VLC_PARAMS
from musicbot.file import File
from musicbot.folders import Folders
from musicbot.helpers import bytes_to_human, precise_seconds_to_human
from musicbot.music_filter import MusicFilter
from musicbot.musicdb import MusicDb
from musicbot.object import MusicbotObject
from musicbot.playlist_options import PlaylistOptions

# from musicbot.watcher import MusicWatcherHandler

logger = logging.getLogger(__name__)


@click.group("local", help="Local music management", cls=AdvancedGroup)
@beartype
def cli() -> None:
    pass


@cli.command(help="EdgeDB raw query", aliases=["query", "fetch"])
@click.argument("query")
@musicdb_options
@beartype
def execute(musicdb: MusicDb, query: str) -> None:
    print(MusicbotObject.async_run(musicdb.query_json(query)))


@cli.command(help="GraphQL query")
@click.argument("query")
@musicdb_options
@beartype
def graphql(musicdb: MusicDb, query: str) -> None:
    response = musicdb.graphql_query(query)
    if response is not None:
        MusicbotObject.print_json(response.json())


@cli.command(help="List folders and some stats")
@musicdb_options
@beartype
def folders(musicdb: MusicDb) -> None:
    response = MusicbotObject.async_run(musicdb.folders())
    if response is not None:
        MusicbotObject.print_json([asdict(folder) for folder in response])


@cli.command(help="Explore with GraphiQL")
@musicdb_options
@beartype
def explore(musicdb: MusicDb) -> None:
    if musicdb.graphql:
        url = f"{musicdb.graphql}/explore"
        MusicbotObject.success(url)
        _ = webbrowser.open(url)


@cli.command(help="Load musics")
@folders_argument
@musicdb_options
@save_option
@output_option
@clean_option
@click.option("--coroutines", help="Limit number of coroutines", default=64, show_default=True)
@beartype
def scan(
    musicdb: MusicDb,
    folders: Folders,
    clean: bool,
    save: bool,
    output: str,
    coroutines: int,
) -> None:
    async def runner() -> list[File]:
        if clean:
            await musicdb.clean_musics()

        files = await musicdb.upsert_folders(
            folders=folders,
            coroutines=coroutines,
        )
        await musicdb.soft_clean()
        return files

    files = MusicbotObject.async_run(runner())

    if output == "json":
        MusicbotObject.print_json([asdict(file.music) for file in files if file.music is not None])

    if save:
        MusicbotObject.config.configfile["musicbot"]["folders"] = folders.unique_directories
        MusicbotObject.config.write()


@cli.command(help="Watch files changes in folders", aliases=["watcher"])
@folders_argument
@musicdb_options
@click.option("--sleep", help="Clean music every X seconds", type=int, default=1800, show_default=True)
@click.option("--timeout", help="How many seconds until we terminate", type=int, show_default=True)
@beartype
def watch(
    musicdb: MusicDb,
    folders: Folders,
    sleep: int,
    timeout: int | None,
) -> None:
    async def soft_clean_periodically() -> None:
        try:
            while True:
                cleaned = await musicdb.soft_clean()
                MusicbotObject.success(cleaned)
                MusicbotObject.success(f"DB cleaned, waiting {sleep} seconds.")
                await asyncio.sleep(sleep)
        except (asyncio.CancelledError, KeyboardInterrupt):
            pass

    class MusicFilter(DefaultFilter):
        def __call__(self, change: Change, path: str) -> bool:
            return super().__call__(change, path) and path.endswith(tuple(folders.extensions))

    async def update_music(path: str) -> None:
        for directory in folders.directories:
            if path.startswith(str(directory)):
                _ = await musicdb.upsert_path((directory, Path(path)))

    async def watcher() -> None:
        try:
            async for changes in awatch(*folders.directories, watch_filter=MusicFilter(), debug=MusicbotObject.config.debug):
                for change_path in changes:
                    change, path = change_path
                    if change in (Change.added, Change.modified):
                        await update_music(path)
                    elif change == Change.deleted:
                        await musicdb.remove_music_path(path)
        except (asyncio.CancelledError, KeyboardInterrupt):
            pass

    async def runner() -> None:
        try:
            _ = await asyncio.wait_for(asyncio.gather(soft_clean_periodically(), watcher()), timeout=timeout)
        except (TimeoutError, asyncio.CancelledError, KeyboardInterrupt):
            pass

    MusicbotObject.async_run(runner())


@cli.command(help="Clean all musics in DB", aliases=["clean-db", "erase"])
@musicdb_options
@yes_option
@beartype
def clean(musicdb: MusicDb) -> None:
    MusicbotObject.async_run(musicdb.clean_musics())


@cli.command(help="Clean entities without musics associated")
@musicdb_options
@beartype
def soft_clean(musicdb: MusicDb) -> None:
    MusicbotObject.async_run(musicdb.soft_clean())


@cli.command(help="Search musics by full-text search")
@musicdb_options
@output_option
@playlist_options
@click.argument("pattern")
@beartype
def search(
    musicdb: MusicDb,
    output: str,
    pattern: str,
    playlist_options: PlaylistOptions,
) -> None:
    p = MusicbotObject.async_run(musicdb.search(pattern))
    p.print(
        output=output,
        playlist_options=playlist_options,
    )


@cli.command(short_help="Generate a new playlist", help=filters_reprs)
@musicdb_options
@output_option
@music_filters_options
@playlist_options
@click.argument("out", type=click.File("w", lazy=True), default="-")
@beartype
def playlist(
    output: str,
    music_filters: list[MusicFilter],
    playlist_options: PlaylistOptions,
    musicdb: MusicDb,
    out: Any,
) -> None:
    musicdb.set_readonly()
    p = MusicbotObject.async_run(
        musicdb.make_playlist(
            music_filters=frozenset(music_filters),
        )
    )
    p.print(
        output=output,
        file=out,
        playlist_options=playlist_options,
    )


@cli.command(short_help="Artists descriptions")
@musicdb_options
@output_option
@beartype
def artists(
    output: str,
    musicdb: MusicDb,
) -> None:
    musicdb.set_readonly()
    all_artists = MusicbotObject.async_run(musicdb.artists())
    table = Table(
        "Name",
        "Rating",
        "Size",
        "Length",
        "Albums",
        "Musics",
        "Keywords",
        "Genres",
        title="Artists",
    )
    for artist in all_artists:
        size = bytes_to_human(artist.size)
        length = precise_seconds_to_human(artist.length)
        table.add_row(
            artist.name,
            str(artist.rating),
            size,
            length,
            str(artist.albums),
            str(artist.musics),
            ", ".join(artist.keywords),
            ", ".join(artist.genres),
        )
    table.caption = f"{len(all_artists)} listed"

    if output == "table":
        MusicbotObject.print_table(table)
    elif output == "json":
        MusicbotObject.print_json([asdict(artist) for artist in all_artists])


@cli.command(short_help="Generate bests playlists with some rules", help=filters_reprs)
@folder_argument
@music_filters_options
@musicdb_options
@dry_option
@playlist_options
@bests_options
@beartype
def bests(
    musicdb: MusicDb,
    music_filters: list[MusicFilter],
    folder: Path,
    min_playlist_size: int,
    playlist_options: PlaylistOptions,
) -> None:
    musicdb.set_readonly()
    bests = MusicbotObject.async_run(
        musicdb.make_bests(
            music_filters=frozenset(music_filters),
        )
    )
    for best in bests:
        if len(best.musics) < min_playlist_size or not best.name:
            MusicbotObject.warn(f"{best.name} : size < {min_playlist_size}")
            continue
        filepath = Path(folder) / (best.name + ".m3u")
        if MusicbotObject.dry:
            MusicbotObject.success(f"DRY RUN: Writing playlist {best.name} to {filepath}")
            continue
        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with codecs.open(str(filepath), "w", "utf-8-sig") as playlist_file:
                best.print(
                    output="m3u",
                    file=playlist_file,
                    playlist_options=playlist_options,
                )
        except (OSError, LookupError, ValueError, UnicodeError) as e:
            logger.warning(f"Unable to write playlist {best.name} to {filepath} because of {e}")

    MusicbotObject.success(f"Playlists: {len(bests)}")


@cli.command(aliases=["play"], short_help="Music player", help=filters_reprs)
@musicdb_options
@music_filters_options
@playlist_options
@click.option("--vlc-params", help="VLC params", default=DEFAULT_VLC_PARAMS, show_default=True)
@beartype
def player(
    music_filters: list[MusicFilter],
    musicdb: MusicDb,
    vlc_params: str,
    playlist_options: PlaylistOptions,
) -> None:
    musicdb.set_readonly()
    if not MusicbotObject.config.quiet or not MusicbotObject.is_test():
        progressbar.streams.unwrap(stderr=True, stdout=True)
    try:
        playlist = MusicbotObject.async_run(
            musicdb.make_playlist(
                music_filters=frozenset(music_filters),
            )
        )
        playlist.play(
            vlc_params=vlc_params,
            playlist_options=playlist_options,
        )
    except io.UnsupportedOperation:
        logger.critical("Unable to load UI")


@cli.command(short_help="Copy selected musics with filters to destination folder", help=filters_reprs)
@destination_argument
@musicdb_options
@lazy_yes_option
@dry_option
@music_filters_options
@flat_option
@click.option("--delete", help="Delete files on destination if not present in library", is_flag=True)
@beartype
def sync(
    musicdb: MusicDb,
    music_filters: list[MusicFilter],
    delete: bool,
    destination: Path,
    yes: bool,
    flat: bool,
) -> None:
    musicdb.set_readonly()
    logger.info(f"Destination: {destination}")
    playlist = MusicbotObject.async_run(
        musicdb.make_playlist(
            music_filters=frozenset(music_filters),
        )
    )
    if not playlist.musics:
        click.secho("no result for filter, nothing to sync")
        return

    folders = Folders(directories=[destination], extensions=set())
    logger.info(f"Files : {len(folders.files)}")
    if not folders.files:
        logger.warning("no files found in destination")

    destinations = {str(path)[len(str(destination)) + 1 :]: path for path in folders.paths}

    musics: list[File] = []
    for music in playlist.musics:
        for link in music.links():
            try:
                path = Path(link)
                music_to_sync = File.from_path(folder=path.parent, path=path)
                if not music_to_sync:
                    continue
                musics.append(music_to_sync)
            except OSError as e:
                logger.error(e)

    logger.info(f"Destinations : {len(destinations)}")
    if flat:
        sources = {music.flat_filename: music.path for music in musics}
    else:
        sources = {str(music.canonic_artist_album_filename): music.path for music in musics}

    logger.info(f"Sources : {len(sources)}")
    paths_to_delete = set(destinations.keys()) - set(sources.keys())
    if delete and (yes or click.confirm(f"Do you really want to delete {len(paths_to_delete)} files and playlists ?")):
        with MusicbotObject.progressbar(max_value=len(paths_to_delete)) as pbar:
            for path_to_delete in paths_to_delete:
                try:
                    final_path_to_delete = Path(destinations[path_to_delete])
                    pbar.desc = f"Deleting musics and playlists: {final_path_to_delete.name}"
                    if MusicbotObject.dry:
                        MusicbotObject.success(f"[DRY-RUN] Deleting {final_path_to_delete}")
                        continue
                    try:
                        MusicbotObject.success(f"Deleting {final_path_to_delete}")
                        final_path_to_delete.unlink()
                    except OSError as e:
                        logger.error(e)
                finally:
                    pbar.value += 1
                    pbar.update()

    to_copy = set(sources.keys()) - set(destinations.keys())
    with MusicbotObject.progressbar(max_value=len(to_copy)) as pbar:
        logger.info(f"To copy: {len(to_copy)}")
        for c in sorted(to_copy):
            final_destination = destination / c
            try:
                path_to_copy = Path(sources[c])
                pbar.desc = f"Copying {path_to_copy.name} to {destination}"
                if MusicbotObject.dry:
                    MusicbotObject.success(f"[DRY-RUN] Copying {path_to_copy.name} to {final_destination}")
                    continue

                MusicbotObject.success(f"Copying {path_to_copy.name} to {final_destination}")
                Path(final_destination).parent.mkdir(exist_ok=True)
                _ = shutil.copyfile(path_to_copy, final_destination)
            except KeyboardInterrupt:
                logger.debug(f"Cleanup {final_destination}")
                try:
                    final_destination.unlink()
                except OSError:
                    pass
                raise
            finally:
                pbar.value += 1
                pbar.update()

    for d in folders.flush_empty_directories():
        if any(e in d for e in folders.except_directories):
            logger.debug(f"Invalid path {d}")
            continue
        if not MusicbotObject.dry:
            shutil.rmtree(d)
        MusicbotObject.success(f"[DRY-RUN] Removing empty dir {d}")
