import asyncio
import codecs
import logging
import shutil
from pathlib import Path

import click

from musicbot import (
    File,
    Issue,
    Music,
    MusicbotObject,
    MusicDb,
    MusicFilter,
    MusicInput,
    PlaylistOptions,
    ScanFolders,
)

logger = logging.getLogger(__name__)


async def playlist(
    output: str,
    music_filters: list[MusicFilter],
    playlist_options: PlaylistOptions,
    musicdb: MusicDb,
    out: click.utils.LazyFile,
) -> None:
    if out.name.endswith(".m3u"):
        output = "m3u"

    new_playlist = await musicdb.make_playlist(
        music_filters=frozenset(music_filters),
    )
    new_playlist.print(
        output=output,
        file=out,
        playlist_options=playlist_options,
    )


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


async def scan(
    musicdb: MusicDb,
    scan_folders: ScanFolders,
) -> list[MusicInput]:
    max_value = len(scan_folders.folders_and_paths)
    if not max_value:
        MusicbotObject.warn(f"No music folder or paths discovered from directories {scan_folders.directories}")
        return []

    MusicbotObject.echo(f"{musicdb} : loading {max_value} files")
    music_inputs = []
    with MusicbotObject.progressbar(desc="Loading files", max_value=max_value) as pbar:
        for folder_and_path in scan_folders.folders_and_paths:
            try:
                folder, path = folder_and_path
                if not (file := File.from_path(folder=folder, path=path)):
                    continue

                issues = file.issues
                if Issue.NO_TITLE in issues or Issue.NO_ARTIST in issues or Issue.NO_ALBUM in issues:
                    MusicbotObject.warn(f"{file} : missing mandatory fields title/album/artist : {issues}")
                    continue
                if not (music_input := file.music_input):
                    MusicbotObject.err(f"{file} : cannot upsert music without physical folder !")
                    continue

                music_inputs.append(music_input)
            finally:
                pbar.value += 1
                _ = pbar.update()

    return music_inputs


async def upsert_musics(
    musicdb: MusicDb,
    music_inputs: list[MusicInput],
) -> list[Music]:
    failed_inputs = []
    music_outputs = []

    with MusicbotObject.progressbar(desc="Inserting musics", max_value=len(music_inputs)) as pbar:

        async def upsert_worker(music_input: MusicInput) -> None:
            try:
                if (music_output := await musicdb.upsert_music(music_input)) is None:
                    MusicbotObject.err(f"{music_input} : unable to insert")
                    failed_inputs.append(music_input)
                else:
                    music_outputs.append(music_output)
            finally:
                pbar.value += 1
                _ = pbar.update()

        async with asyncio.TaskGroup() as tg:
            for music_input in music_inputs:
                _ = tg.create_task(upsert_worker(music_input))

    if failed_inputs:
        MusicbotObject.warn(f"Unable to insert {len(failed_inputs)} files")
    return music_outputs


async def sync(
    musicdb: MusicDb,
    music_filters: list[MusicFilter],
    delete: bool,
    destination: Path,
    yes: bool,
    flat: bool,
) -> None:
    logger.info(f"Destination: {destination}")
    sync_playlist = await musicdb.make_playlist(
        music_filters=frozenset(music_filters),
    )
    if not sync_playlist.musics:
        MusicbotObject.echo("no result for filter, nothing to sync")
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
