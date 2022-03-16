# import codecs
import io
import logging
import shutil
import time
from pathlib import Path

import click
import progressbar  # type: ignore
from attr import evolve
from beartype import beartype
from click_skeleton import AdvancedGroup
from watchdog.observers import Observer  # type: ignore

from musicbot.cli.file import flat_option
from musicbot.cli.folders import (
    destination_argument,
    folder_argument,
    folders_argument
)
from musicbot.cli.link_options import link_options_options
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
from musicbot.cli.playlist import bests_options
from musicbot.file import File
from musicbot.folders import Folders
from musicbot.link_options import LinkOptions
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
    print(musicdb.blocking_client.query_json(query))


@cli.command(help='Load musics')
@folders_argument
@musicdb_options
@save_option
@output_option
@clean_option
@link_options_options
@beartype
def scan(
    musicdb: MusicDb,
    folders: Folders,
    clean: bool,
    save: bool,
    link_options: LinkOptions,
    output: str,
) -> None:
    if clean:
        musicdb.clean_musics()

    musics = musicdb.upsert_folders(
        folders=folders,
        link_options=link_options,
    )
    if output == 'json':
        MusicbotObject.print_json(musics)

    if save:
        MusicbotObject.config.configfile['musicbot']['folders'] = folders.unique_directories
        MusicbotObject.config.write()


@cli.command(help='Watch files changes in folders')
@folders_argument
@musicdb_options
@beartype
def watch(
    musicdb: MusicDb,
    folders: Folders,
) -> None:
    event_handler = MusicWatcherHandler(musicdb=musicdb, folders=folders)
    observer = Observer()
    for path in folders.paths:
        observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(50)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


@cli.command(help='Clean all musics')
@musicdb_options
@yes_option
@beartype
def clean(musicdb: MusicDb) -> None:
    musicdb.clean_musics()


@cli.command(help='Generate a new playlist')
@musicdb_options
@output_option
@link_options_options
@music_filter_options
@beartype
def playlist(
    output: str,
    music_filter: MusicFilter,
    link_options: LinkOptions,
    musicdb: MusicDb,
) -> None:
    p = musicdb.make_playlist(
        music_filter=music_filter,
        link_options=link_options,
    )
    p.print(output=output)


@cli.command(help='Generate bests playlists with some rules')
@folder_argument
@music_filter_options
@musicdb_options
@dry_option
@link_options_options
@bests_options
@beartype
def bests(
    musicdb: MusicDb,
    music_filter: MusicFilter,
    link_options: LinkOptions,
    folder: Path,
    min_playlist_size: int,
    ratings: tuple[float, ...],
    types: list[str],
) -> None:
    prefiltered = musicdb.make_playlist(music_filter=music_filter, link_options=link_options)
    if "genre" in types and prefiltered.genres:
        with MusicbotObject.progressbar(max_value=len(prefiltered.genres), prefix="Generating bests genres") as pbar:
            for genre in prefiltered.genres:
                try:
                    filter_copy = evolve(
                        music_filter,
                        genres=frozenset([genre]),
                    )
                    best = musicdb.make_playlist(music_filter=filter_copy, link_options=link_options)
                    if len(best.musics) < min_playlist_size:
                        continue
                    filepath = Path(folder) / ('genre_' + genre.lower() + '.m3u')
                    best.write(filepath)
                finally:
                    pbar.value += 1
                    pbar.update()

    if "rating" in types and ratings:
        with MusicbotObject.progressbar(max_value=len(ratings), prefix="Generating bests ratings") as pbar:
            for rating in ratings:
                try:
                    filter_copy = evolve(
                        music_filter,
                        min_rating=rating,
                    )
                    best = musicdb.make_playlist(music_filter=filter_copy, link_options=link_options)
                    if len(best.musics) < min_playlist_size:
                        continue
                    filepath = Path(folder) / ('rating_' + str(rating) + '.m3u')
                    best.write(filepath)
                finally:
                    pbar.value += 1
                    pbar.update()

    if "keyword" in types and prefiltered.keywords:
        with MusicbotObject.progressbar(max_value=len(prefiltered.keywords), prefix="Generating bests keywords") as pbar:
            for keyword in prefiltered.keywords:
                try:
                    filter_copy = evolve(
                        music_filter,
                        keywords=frozenset([keyword]),
                    )
                    best = musicdb.make_playlist(music_filter=filter_copy, link_options=link_options)
                    if len(best.musics) < min_playlist_size:
                        continue
                    filepath = Path(folder) / ('keyword_' + keyword.lower() + '.m3u')
                    best.write(filepath)
                finally:
                    pbar.value += 1
                    pbar.update()

    if "artist" not in types:
        return

    def worker(artist: str) -> None:
        if "rating" in types and ratings:
            for rating in ratings:
                filter_copy = evolve(
                    music_filter,
                    min_rating=rating,
                    artists=frozenset([artist]),
                )
                best = musicdb.make_playlist(music_filter=filter_copy, link_options=link_options)
                if len(best.musics) < min_playlist_size:
                    continue
                filepath = Path(folder) / artist / ('rating_' + str(rating) + '.m3u')
                best.write(filepath)

        if "keyword" in types and prefiltered.keywords:
            for keyword in prefiltered.keywords:
                filter_copy = evolve(
                    music_filter,
                    keywords=frozenset([keyword]),
                    artists=frozenset([artist]),
                )
                best = musicdb.make_playlist(music_filter=filter_copy, link_options=link_options)
                if len(best.musics) < min_playlist_size:
                    continue
                filepath = Path(folder) / artist / ('keyword_' + keyword.lower() + '.m3u')
                best.write(filepath)

    MusicbotObject.parallel(worker, list(prefiltered.artists), prefix="Generating bests artists")


@cli.command(aliases=['play'], help='Music player')
@musicdb_options
@music_filter_options
@beartype
def player(music_filter: MusicFilter, musicdb: MusicDb) -> None:
    if not MusicbotObject.config.quiet:
        progressbar.streams.unwrap(stderr=True, stdout=True)
    try:
        playlist = musicdb.make_playlist(music_filter)
        playlist.play()
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
    logger.info(f'Destination: {destination}')
    playlist = musicdb.make_playlist(music_filter)
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
        for link in music.links:
            try:
                if link.startswith('ssh://'):
                    continue
                music_to_sync = File.from_path(Path(link))
                musics.append(music_to_sync)
            except OSError as e:
                logger.error(e)

    logger.info(f"Destinations : {len(destinations)}")
    if flat:
        sources = {music.flat_filename: music.path for music in musics}
    else:
        sources = {music.filename: music.path for music in musics}

    logger.info(f"Sources : {len(sources)}")
    to_delete = set(destinations.keys()) - set(sources.keys())
    if delete and (yes or click.confirm(f'Do you really want to delete {len(to_delete)} files and playlists ?')):
        with MusicbotObject.progressbar(max_value=len(to_delete)) as pbar:
            for d in to_delete:
                try:
                    path_to_delete = Path(destinations[d])
                    pbar.desc = f"Deleting musics and playlists: {path_to_delete.name}"
                    if MusicbotObject.dry:
                        logger.info(f"[DRY-RUN] Deleting {path_to_delete}")
                        continue
                    try:
                        logger.info(f"Deleting {path_to_delete}")
                        path_to_delete.unlink()
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
                    logger.info(f"[DRY-RUN] Copying {path_to_copy.name} to {final_destination}")
                    continue
                logger.info(f"Copying {path_to_copy.name} to {final_destination}")

                Path(final_destination).parent.mkdir(exist_ok=True)
                shutil.copyfile(path_to_copy, final_destination)
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
        logger.info(f"[DRY-RUN] Removing empty dir {d}")
