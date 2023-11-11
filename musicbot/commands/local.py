import asyncio
import codecs
import io
import logging
import shutil
from dataclasses import asdict
from pathlib import Path
from typing import Any

import click
import edgedb
import progressbar  # type: ignore
from beartype import beartype
from click_skeleton import AdvancedGroup
from rich.table import Table
from watchfiles import Change, DefaultFilter, awatch

from musicbot import (
    File,
    MusicbotObject,
    MusicDb,
    MusicFilter,
    PlaylistOptions,
    ScanFolders,
    syncify,
)
from musicbot.cli.file import flat_option
from musicbot.cli.music_filter import filters_reprs, music_filters_options
from musicbot.cli.musicdb import musicdb_options
from musicbot.cli.options import (
    clean_option,
    dry_option,
    lazy_yes_option,
    output_option,
    save_option,
)
from musicbot.cli.playlist import bests_options, playlist_options
from musicbot.cli.scan_folders import (
    destination_argument,
    scan_folder_argument,
    scan_folders_argument,
)
from musicbot.defaults import DEFAULT_VLC_PARAMS

logger = logging.getLogger(__name__)


@click.group("local", help="Local music management", cls=AdvancedGroup)
@beartype
def cli() -> None:
    pass


@cli.command(help="List folders and some stats")
@musicdb_options
@output_option
@syncify
@beartype
async def folders(musicdb: MusicDb, output: str) -> None:
    all_folders = await musicdb.folders()

    table = Table(
        "Name",
        "IPv4",
        "Size",
        "Length",
        "Genres",
        "Artists",
        "Albums",
        "Musics",
        "Keywords",
        title="Folders",
    )
    for folder in all_folders:
        table.add_row(
            folder.name,
            folder.ipv4,
            folder.human_size,
            folder.human_duration,
            str(folder.n_genres),
            str(folder.n_artists),
            str(folder.n_albums),
            str(folder.n_musics),
            str(folder.n_keywords),
        )
    table.caption = f"{len(all_folders)} listed"

    if output == "table":
        MusicbotObject.print_table(table)
    elif output == "json":
        MusicbotObject.print_json([asdict(folder) for folder in all_folders])


@cli.command(help="Remove one or more music", aliases=["delete"])
@click.argument("files", nargs=-1)
@musicdb_options
@syncify
@beartype
async def remove(
    files: tuple[str, ...],
    musicdb: MusicDb,
) -> None:
    for file in files:
        _ = await musicdb.remove_music_path(file)


@cli.command(help="Clean all musics", aliases=["wipe"])
@musicdb_options
@syncify
@beartype
async def clean(
    musicdb: MusicDb,
) -> None:
    _ = await musicdb.clean_musics()


@cli.command(help="Load musics")
@scan_folders_argument
@musicdb_options
@save_option
@output_option
@clean_option
@click.option("--coroutines", help="Limit number of coroutines", default=64, show_default=True)
@syncify
@beartype
async def scan(
    musicdb: MusicDb,
    scan_folders: ScanFolders,
    clean: bool,
    save: bool,
    output: str,
    coroutines: int,
) -> None:
    # MusicbotObject.success(f"Opening EdgeDB on {MusicbotObject.public_ip()}")
    # _ = subprocess.run(
    #     [
    #         "edgedb",
    #         "configure",
    #         "set",
    #         "listen_addresses",
    #         "127.0.0.1",
    #         "::1",
    #         MusicbotObject.public_ip(),
    #     ],
    #     check=False,
    # )
    if clean:
        _ = await musicdb.clean_musics()

    files = await musicdb.upsert_folders(
        scan_folders=scan_folders,
        coroutines=coroutines,
    )
    _ = await musicdb.soft_clean()

    if output == "json":
        MusicbotObject.print_json([asdict(file.music) for file in files if file.music is not None])

    if save:
        MusicbotObject.config.configfile["musicbot"]["folders"] = folders.unique_directories
        MusicbotObject.config.write()


@cli.command(help="Watch files changes in folders", aliases=["watcher"])
@scan_folders_argument
@musicdb_options
@click.option("--sleep", help="Clean music every X seconds", type=int, default=1800, show_default=True)
@click.option("--timeout", help="How many seconds until we terminate", type=int, show_default=True)
@syncify
@beartype
async def watch(
    musicdb: MusicDb,
    scan_folders: ScanFolders,
    sleep: int,
    timeout: int | None,
) -> None:
    async def soft_clean_periodically() -> None:
        try:
            while True:
                try:
                    cleaned = await musicdb.soft_clean()
                    MusicbotObject.success(cleaned)
                    MusicbotObject.success(f"DB cleaned, waiting {sleep} seconds.")
                    await asyncio.sleep(sleep)
                except edgedb.ClientConnectionFailedTemporarilyError as error:
                    MusicbotObject.err(f"{musicdb} : unable to clean musics", error=error)
        except (asyncio.CancelledError, KeyboardInterrupt):
            pass

    async def update_music(path: str) -> None:
        for directory in scan_folders.directories:
            if path.startswith(str(directory)):
                _ = await musicdb.upsert_path((directory, Path(path)))

    async def watcher() -> None:
        class MusicWatchFilter(DefaultFilter):
            def __call__(self, change: Change, path: str) -> bool:
                return super().__call__(change, path) and path.endswith(tuple(scan_folders.extensions))

        try:
            async for changes in awatch(
                *scan_folders.directories,
                watch_filter=MusicWatchFilter(),
                debug=MusicbotObject.config.debug,
            ):
                try:
                    for change_path in changes:
                        change, path = change_path
                        if change in (Change.added, Change.modified):
                            await update_music(path)
                        elif change == Change.deleted:
                            _ = await musicdb.remove_music_path(path)
                except edgedb.ClientConnectionFailedTemporarilyError as error:
                    MusicbotObject.err(f"{musicdb} : unable to clean musics", error=error)
        except (asyncio.CancelledError, KeyboardInterrupt):
            pass

    try:
        future = asyncio.gather(
            soft_clean_periodically(),
            watcher(),
        )
        _ = await asyncio.wait_for(future, timeout=timeout)
    except (TimeoutError, asyncio.CancelledError, KeyboardInterrupt):
        pass


@cli.command(short_help="Generate a new playlist", help=filters_reprs)
@musicdb_options
@output_option
@music_filters_options
@playlist_options
@click.argument("out", type=click.File("w", lazy=True), default="-")
@syncify
@beartype
async def playlist(
    output: str,
    music_filters: list[MusicFilter],
    playlist_options: PlaylistOptions,
    musicdb: MusicDb,
    out: Any,
) -> None:
    musicdb.set_readonly()
    new_playlist = await musicdb.make_playlist(
        music_filters=frozenset(music_filters),
    )
    new_playlist.print(
        output=output,
        file=out,
        playlist_options=playlist_options,
    )


@cli.command(short_help="Artists descriptions")
@musicdb_options
@output_option
@syncify
@beartype
async def artists(
    output: str,
    musicdb: MusicDb,
) -> None:
    musicdb.set_readonly()
    all_artists = await musicdb.artists()
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
        table.add_row(
            artist.name,
            str(artist.rating),
            artist.human_size,
            artist.human_duration,
            str(artist.n_albums),
            str(artist.n_musics),
            artist.all_keywords,
            artist.all_genres,
        )
    table.caption = f"{len(all_artists)} listed"

    if output == "table":
        MusicbotObject.print_table(table)
    elif output == "json":
        MusicbotObject.print_json([asdict(artist) for artist in all_artists])


@cli.command(short_help="Generate bests playlists with some rules", help=filters_reprs)
@scan_folder_argument
@music_filters_options
@musicdb_options
@dry_option
@playlist_options
@bests_options
@syncify
@beartype
async def bests(
    musicdb: MusicDb,
    music_filters: list[MusicFilter],
    scan_folder: Path,
    min_playlist_size: int,
    playlist_options: PlaylistOptions,
) -> None:
    musicdb.set_readonly()
    bests = await musicdb.make_bests(
        music_filters=frozenset(music_filters),
    )
    for best in bests:
        if len(best.musics) < min_playlist_size or not best.name:
            MusicbotObject.warn(f"{best.name} : size < {min_playlist_size}")
            continue
        filepath = Path(scan_folder) / (best.name + ".m3u")
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
@syncify
@beartype
async def player(
    music_filters: list[MusicFilter],
    musicdb: MusicDb,
    vlc_params: str,
    playlist_options: PlaylistOptions,
) -> None:
    musicdb.set_readonly()
    if not MusicbotObject.config.quiet or not MusicbotObject.is_test():
        progressbar.streams.unwrap(stderr=True, stdout=True)
    try:
        new_playlist = await musicdb.make_playlist(
            music_filters=frozenset(music_filters),
        )
        new_playlist.play(
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
@syncify
@beartype
async def sync(
    musicdb: MusicDb,
    music_filters: list[MusicFilter],
    delete: bool,
    destination: Path,
    yes: bool,
    flat: bool,
) -> None:
    musicdb.set_readonly()
    logger.info(f"Destination: {destination}")
    sync_playlist = await musicdb.make_playlist(
        music_filters=frozenset(music_filters),
    )
    if not sync_playlist.musics:
        click.secho("no result for filter, nothing to sync")
        return

    scan_folders = ScanFolders(directories=[destination], extensions=frozenset())
    logger.info(f"Files : {len(scan_folders.files)}")
    if not scan_folders.files:
        logger.warning("no files found in destination")

    destinations = {str(path)[len(str(destination)) + 1 :]: path for path in scan_folders.paths}

    musics: list[File] = []
    for music in sync_playlist.musics:
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
                    _ = pbar.update()

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
                _ = pbar.update()

    for d in scan_folders.flush_empty_directories():
        if any(e in d for e in scan_folders.except_directories):
            logger.debug(f"Invalid path {d}")
            continue
        if not MusicbotObject.dry:
            shutil.rmtree(d)
        MusicbotObject.success(f"[DRY-RUN] Removing empty dir {d}")
