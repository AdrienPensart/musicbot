import itertools
import json
import logging
import random
from pathlib import Path

import click
import mutagen  # type: ignore
from beartype import beartype
from click_skeleton import AdvancedGroup
from click_skeleton.helpers import PrettyDefaultDict
from rich.table import Table

from musicbot.cli.file import (
    checks_and_fix_options,
    flat_option,
    keywords_arguments
)
from musicbot.cli.folders import destination_argument, folders_argument
from musicbot.cli.music_filter import ordering_options
from musicbot.cli.options import dry_option, output_option, threads_option
from musicbot.exceptions import MusicbotError
from musicbot.file import File
from musicbot.folders import Folders
from musicbot.object import MusicbotObject

logger = logging.getLogger(__name__)


@click.group('folder', help='Manage folders', cls=AdvancedGroup)
@beartype
def cli() -> None:
    pass


@cli.command(help='Just list music files')
@folders_argument
@beartype
def find(folders: Folders) -> None:
    for file in folders.files:
        print(file)


@cli.command(help='Generate a playlist', aliases=['tracks'])
@folders_argument
@output_option
@ordering_options
@beartype
def playlist(
    folders: Folders,
    output: str,
    shuffle: bool,
    interleave: bool,
) -> None:
    if interleave:
        tracks_by_artist = PrettyDefaultDict(list)
        for music in folders.musics:
            tracks_by_artist[music.artist].append(music)
        tracks = [
            track
            for track in itertools.chain(*itertools.zip_longest(*tracks_by_artist.values()))
            if track is not None
        ]

    if shuffle:
        random.shuffle(tracks)

    if output == 'm3u':
        p = '#EXTM3U\n'
        p += '\n'.join([track.path for track in tracks])
        print(p)
        return

    if output == 'json':
        tracks_dict = [{'title': t.title, 'artist': t.artist, 'album': t.album} for t in tracks]
        print(json.dumps(tracks_dict))
        return

    if output == 'table':
        table = Table("Track", "Title", "Artist", "Album")
        for t in tracks:
            table.add_row(str(t.track), t.title, t.artist, t.album)
        MusicbotObject.console.print(table)


@cli.command(help='Print music tags')
@folders_argument
@beartype
def tags(folders: Folders) -> None:
    for music in folders.musics:
        logger.info(music.handle.tags.keys())
        print(music.to_dict())


@cli.command(help='Convert all files in folders to mp3')
@destination_argument
@folders_argument
@threads_option
@dry_option
@flat_option
@beartype
def flac2mp3(
    folders: Folders,
    destination: Path,
    threads: int,
    flat: bool,
) -> None:
    folders.extensions = {'flac'}
    if not folders.files:
        logger.warning(f"No flac files detected in {folders}")
        return

    def worker(music: File) -> None:
        try:
            music.to_mp3(flat=flat, destination=destination)
        except MusicbotError as e:
            logger.error(e)
        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"{music} : unable to convert to mp3 : {e}")

    folders.apply(
        worker,
        prefix="Converting flac to mp3",
        threads=threads,
    )


@cli.command(aliases=['consistency'], help='Check music files consistency')
@folders_argument
@dry_option
@checks_and_fix_options
@beartype
def inconsistencies(
    folders: Folders,
    fix: bool,
    checks: list[str],
) -> None:
    table = Table("Path", "Inconsistencies")
    for music in folders.musics:
        try:
            if fix:
                music.fix(checks=checks)
            if music.inconsistencies.intersection(set(checks)):
                table.add_row(str(music.path), ', '.join(music.inconsistencies))
        except (OSError, mutagen.MutagenError):
            table.add_row(str(music.path), "could not open file")
    MusicbotObject.console.print(table)


@cli.command(help='Add keywords to music')
@dry_option
@folders_argument
@keywords_arguments
@beartype
def add_keywords(
    folders: Folders,
    keywords: set[str],
) -> None:
    for music in folders.musics:
        music.add_keywords(keywords)


@cli.command(help='Delete keywords to music')
@dry_option
@folders_argument
@keywords_arguments
@beartype
def delete_keywords(
    folders: Folders,
    keywords: set[str],
) -> None:
    for music in folders.musics:
        music.delete_keywords(keywords)
