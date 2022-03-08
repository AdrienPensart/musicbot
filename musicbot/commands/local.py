# import codecs
import io
import logging
import shutil
import time
from pathlib import Path

import attr
import click
import progressbar  # type: ignore
from beartype import beartype
from click_skeleton import AdvancedGroup
from watchdog.observers import Observer  # type: ignore

from musicbot.cli.file import extensions_option, flat_option
from musicbot.cli.folders import (
    destination_argument,
    folder_argument,
    folders_argument
)
from musicbot.cli.music_filter import link_options, music_filter_options
from musicbot.cli.musicdb import musicdb_options
from musicbot.cli.options import (
    clean_option,
    dry_option,
    output_option,
    sane_list,
    save_option,
    threads_option,
    yes_option
)
from musicbot.defaults import EXCEPT_DIRECTORIES
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
    print(musicdb.client.query_json(query))


@cli.command(help='Load musics')
@folders_argument
@musicdb_options
@extensions_option
@save_option
@clean_option
@link_options
@threads_option
@beartype
def scan(
    musicdb: MusicDb,
    clean: bool,
    save: bool,
    folders: list[Path],
    extensions: list[str],
    http: bool,
    sftp: bool,
    youtube: bool,
    spotify: bool,
    local: bool,
    threads: int,
) -> None:
    if clean:
        musicdb.clean_musics()

    def worker(music: File) -> None:
        try:
            if 'no-title' in music.inconsistencies or 'no-artist' in music.inconsistencies or 'no-album' in music.inconsistencies:
                MusicbotObject.warn(f"{music} : missing mandatory fields title/album/artist : {music.inconsistencies}")
                return

            musicdb.upsert_music(
                music,
                http=http,
                sftp=sftp,
                youtube=youtube,
                spotify=spotify,
                local=local,
            )
        except Exception as e:  # pylint: disable=broad-except
            MusicbotObject.err(f"{music} : {music.rating} - unable to upsert music : {e}")

    musics = Folders(folders=folders, extensions=extensions).musics
    MusicbotObject.parallel(
        worker,
        musics,
        prefix="Upserting music",
        threads=threads,
    )
    if save:
        MusicbotObject.config.configfile['musicbot']['folders'] = ','.join({str(folder) for folder in folders})
        MusicbotObject.config.write()


@cli.command(help='Watch files changes in folders')
@folders_argument
@extensions_option
@musicdb_options
@beartype
def watch(
    musicdb: MusicDb,
    folders: list[Path],
    extensions: list[str],
) -> None:
    event_handler = MusicWatcherHandler(musicdb=musicdb, folders=folders, extensions=extensions)
    observer = Observer()
    for folder in folders:
        observer.schedule(event_handler, folder, recursive=True)
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
@link_options
@music_filter_options
@beartype
def playlist(
    output: str,
    music_filter: MusicFilter,
    musicdb: MusicDb,
) -> None:
    p = musicdb.make_playlist(music_filter)
    p.print(output=output)


@cli.command(help='Generate bests playlists with some rules')
@click.option('--min-playlist-size', help="Minimum size of playlist to write", default=1)
@click.option('--ratings', help="Generate bests for those ratings", default=[4.0, 4.5, 5.0], multiple=True, callback=sane_list)
@click.option('--types', help="Type of bests playlists", default=["genre", "keyword", "rating", "artist"], multiple=True, callback=sane_list)
@folder_argument
@dry_option
@music_filter_options
@musicdb_options
@beartype
def bests(
    musicdb: MusicDb,
    music_filter: MusicFilter,
    folder: Path,
    min_playlist_size: int,
    ratings: list[float],
    types: list[str],
) -> None:
    prefiltered = musicdb.make_playlist(music_filter)
    if "genre" in types:
        with MusicbotObject.progressbar(max_value=len(prefiltered.genres), prefix="Generating bests genres") as pbar:
            for genre in prefiltered.genres:
                try:
                    filter_copy = attr.evolve(
                        music_filter,
                        genres=frozenset([genre]),
                    )
                    best = musicdb.make_playlist(filter_copy)
                    if len(best.musics) < min_playlist_size:
                        continue
                    filepath = Path(folder) / ('genre_' + genre.lower() + '.m3u')
                    best.write(filepath)
                finally:
                    pbar.value += 1
                    pbar.update()

    if "rating" in types:
        with MusicbotObject.progressbar(max_value=len(ratings), prefix="Generating bests ratings") as pbar:
            for rating in ratings:
                try:
                    filter_copy = attr.evolve(
                        music_filter,
                        min_rating=rating,
                    )
                    best = musicdb.make_playlist(filter_copy)
                    if len(best.musics) < min_playlist_size:
                        continue
                    filepath = Path(folder) / ('rating_' + str(rating) + '.m3u')
                    best.write(filepath)
                finally:
                    pbar.value += 1
                    pbar.update()

    if "keyword" in types:
        with MusicbotObject.progressbar(max_value=len(prefiltered.keywords), prefix="Generating bests keywords") as pbar:
            for keyword in prefiltered.keywords:
                try:
                    filter_copy = attr.evolve(
                        music_filter,
                        keywords=frozenset([keyword]),
                    )
                    best = musicdb.make_playlist(filter_copy)
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
        if "rating" in types:
            for rating in ratings:
                filter_copy = attr.evolve(
                    music_filter,
                    min_rating=rating,
                    artists=frozenset([artist]),
                )
                best = musicdb.make_playlist(filter_copy)
                if len(best.musics) < min_playlist_size:
                    continue
                filepath = Path(folder) / artist / ('rating_' + str(rating) + '.m3u')
                best.write(filepath)

        if "keyword" in types:
            for keyword in prefiltered.keywords:
                filter_copy = attr.evolve(
                    music_filter,
                    keywords=frozenset([keyword]),
                    artists=frozenset([artist]),
                )
                best = musicdb.make_playlist(filter_copy)
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
@dry_option
@click.option('--yes', '-y', help="Confirm file deletion on destination", is_flag=True)
@musicdb_options
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

    folders = Folders(folders=[destination], extensions=[])
    logger.info(f"Files : {len(folders.files)}")
    if not folders.files:
        logger.warning("no files found in destination")

    destinations = {str(file)[len(str(destination)) + 1:]: file for file in folders.files}

    musics: list[File] = []
    for music in playlist.musics:
        for link in music.links:
            try:
                if link.startswith('ssh://'):
                    continue
                musics.append(File(path=Path(link)))
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

    for d in folders.empty_dirs():
        if any(e in d for e in EXCEPT_DIRECTORIES):
            logger.debug(f"Invalid path {d}")
            continue
        if not MusicbotObject.dry:
            shutil.rmtree(d)
        logger.info(f"[DRY-RUN] Removing empty dir {d}")
