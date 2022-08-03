import codecs
import io
import logging
import shutil
import threading
import time
from pathlib import Path
from typing import Any

import click
import progressbar  # type: ignore
from attr import asdict
from beartype import beartype
from click_skeleton import AdvancedGroup
from watchdog.observers import Observer  # type: ignore

from musicbot.cli.file import flat_option
from musicbot.cli.folders import (
    destination_argument,
    folder_argument,
    folders_argument
)
from musicbot.cli.music_filter import music_filter_options
from musicbot.cli.musicdb import musicdb_options
from musicbot.cli.options import (
    clean_option,
    dry_option,
    lazy_yes_option,
    output_option,
    save_option,
    yes_option
)
from musicbot.cli.playlist import bests_options, links_option
from musicbot.defaults import DEFAULT_VLC_PARAMS
from musicbot.file import File
from musicbot.folders import Folders
from musicbot.music_filter import MusicFilter
from musicbot.musicdb import MusicDb
from musicbot.object import MusicbotObject
from musicbot.watcher import MusicWatcherHandler

logger = logging.getLogger(__name__)


@click.group('local', help='Local music management', cls=AdvancedGroup)
@beartype
def cli() -> None:
    pass


@cli.command(help='Raw query', aliases=['query', 'fetch'])
@click.argument('query')
@musicdb_options
@beartype
def execute(musicdb: MusicDb, query: str) -> None:
    print(musicdb.sync_query(query))


@cli.command(help='Load musics')
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
    if clean:
        musicdb.sync_clean_musics()

    files = musicdb.sync_upsert_folders(
        folders=folders,
        coroutines=coroutines,
    )
    if output == 'json':
        MusicbotObject.print_json([asdict(file.to_music()) for file in files])

    if save:
        MusicbotObject.config.configfile['musicbot']['folders'] = folders.unique_directories
        MusicbotObject.config.write()


@cli.command(help='Watch files changes in folders', aliases=['watcher'])
@folders_argument
@musicdb_options
@click.option('--sleep', help="Clean music every X seconds", type=int, default=3600, show_default=True)
@click.option('--timeout', help="How many seconds until we terminate", type=int, show_default=True)
@beartype
def watch(
    musicdb: MusicDb,
    folders: Folders,
    sleep: int,
    timeout: int | None,
) -> None:
    def soft_clean_periodically() -> None:
        try:
            while True:
                musicdb.sync_soft_clean()
                time.sleep(sleep)
        except KeyboardInterrupt:
            pass

    periodic_soft_clean = threading.Thread(target=soft_clean_periodically, daemon=True)
    periodic_soft_clean.start()

    event_handler = MusicWatcherHandler(musicdb=musicdb, folders=folders)
    observer = Observer()
    for directory in folders.directories:
        observer.schedule(event_handler, directory, recursive=True)
        MusicbotObject.success(f"{directory} : watching")
    observer.start()
    observer.join(timeout=timeout)


@cli.command(help='Clean all musics in DB', aliases=["clean-db", "erase"])
@musicdb_options
@yes_option
@beartype
def clean(musicdb: MusicDb) -> None:
    musicdb.sync_clean_musics()


@cli.command(help='Clean entities without musics associated')
@musicdb_options
@beartype
def soft_clean(musicdb: MusicDb) -> None:
    musicdb.sync_soft_clean()


@cli.command(help='Search musics by full-text search')
@musicdb_options
@output_option
@links_option
@click.argument('pattern')
@beartype
def search(
    musicdb: MusicDb,
    output: str,
    pattern: str,
    links: list[str],
) -> None:
    p = musicdb.sync_search(pattern)
    p.print(output=output, types=links)


@cli.command(help='Generate a new playlist')
@musicdb_options
@output_option
@music_filter_options
@links_option
@click.argument('out', type=click.File('w', lazy=True), default='-')
@beartype
def playlist(
    output: str,
    music_filter: MusicFilter,
    musicdb: MusicDb,
    out: Any,
    links: list[str],
) -> None:
    musicdb.set_readonly()
    p = musicdb.sync_make_playlist(
        music_filter=music_filter,
    )
    p.print(output=output, file=out, types=links)


@cli.command(help='Generate bests playlists with some rules')
@folder_argument
@music_filter_options
@musicdb_options
@dry_option
@links_option
@bests_options
@beartype
def bests(
    musicdb: MusicDb,
    music_filter: MusicFilter,
    folder: Path,
    min_playlist_size: int,
    links: list[str],
) -> None:
    musicdb.set_readonly()
    bests = musicdb.sync_make_bests(
        music_filter=music_filter,
    )
    for best in bests:
        if len(best.musics) < min_playlist_size:
            return
        if best.name:
            filepath = Path(folder) / (best.name + '.m3u')
            if MusicbotObject.dry:
                MusicbotObject.success(f'DRY RUN: Writing playlist {best.name} to {filepath}')
                continue
            try:
                filepath.parent.mkdir(parents=True, exist_ok=True)
                with codecs.open(str(filepath), 'w', "utf-8-sig") as playlist_file:
                    best.print(output="m3u", file=playlist_file, types=links)
            except (OSError, LookupError, ValueError, UnicodeError) as e:
                logger.warning(f'Unable to write playlist {best.name} to {filepath} because of {e}')

    MusicbotObject.success(f"Playlists: {len(bests)}")


@cli.command(aliases=['play'], help='Music player')
@musicdb_options
@links_option
@music_filter_options
@click.option('--vlc-params', help="VLC params", default=DEFAULT_VLC_PARAMS, show_default=True)
@beartype
def player(
    music_filter: MusicFilter,
    musicdb: MusicDb,
    vlc_params: str,
    links: list[str],
) -> None:
    musicdb.set_readonly()
    if not MusicbotObject.config.quiet:
        progressbar.streams.unwrap(stderr=True, stdout=True)
    try:
        playlist = musicdb.sync_make_playlist(music_filter=music_filter)
        playlist.play(vlc_params=vlc_params, types=links)
    except io.UnsupportedOperation:
        logger.critical('Unable to load UI')


@cli.command(help='Copy selected musics with filters to destination folder')
@destination_argument
@musicdb_options
@lazy_yes_option
@dry_option
@music_filter_options
@flat_option
@click.option('--delete', help='Delete files on destination if not present in library', is_flag=True)
@beartype
def sync(
    musicdb: MusicDb,
    music_filter: MusicFilter,
    delete: bool,
    destination: Path,
    yes: bool,
    flat: bool,
) -> None:
    musicdb.set_readonly()
    logger.info(f'Destination: {destination}')
    playlist = musicdb.sync_make_playlist(music_filter=music_filter)
    if not playlist.musics:
        click.secho('no result for filter, nothing to sync')
        return

    folders = Folders(directories=[destination], extensions=set())
    logger.info(f"Files : {len(folders.files)}")
    if not folders.files:
        logger.warning("no files found in destination")

    destinations = {str(path)[len(str(destination)) + 1:]: path for path in folders.paths}

    musics: list[File] = []
    for music in playlist.musics:
        for link in music.links(types=['local']):
            try:
                path = Path(link)
                music_to_sync = File.from_path(folder=path.parent, path=path)
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
    if delete and (yes or click.confirm(f'Do you really want to delete {len(paths_to_delete)} files and playlists ?')):
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
                pbar.desc = f'Copying {path_to_copy.name} to {destination}'
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
