from typing import List, Tuple
from pathlib import Path
import logging
import json
import random
import itertools
import click
import mutagen  # type: ignore
from rich.table import Table
from beartype import beartype
from click_skeleton import AdvancedGroup
from click_skeleton.helpers import PrettyDefaultDict
from musicbot.cli.options import output_option, concurrency_options, dry_option
from musicbot.cli.music_filter import ordering_options
from musicbot.cli.file import keywords_argument, flat_option, checks_and_fix_options, extensions_option
from musicbot.cli.folders import destination_argument, folders_argument

from musicbot.object import MusicbotObject
from musicbot.exceptions import MusicbotError
from musicbot.music.folders import Folders
from musicbot.music.file import File

logger = logging.getLogger(__name__)


@click.group('folder', help='Manage folders', cls=AdvancedGroup)
@beartype
def cli() -> None:
    pass


@cli.command(help='Just list music files')
@folders_argument
@extensions_option
@beartype
def find(folders: Tuple[Path, ...], extensions: Tuple[str, ...]) -> None:
    files = Folders(folders=folders, extensions=extensions).files
    for file in files:
        print(file)


@cli.command(help='Generate a playlist', aliases=['tracks'])
@folders_argument
@output_option
@ordering_options
@extensions_option
@beartype
def playlist(folders: Tuple[Path, ...], extensions: Tuple[str, ...], output: str, shuffle: bool, interleave: bool) -> None:
    tracks = Folders(folders=folders, extensions=extensions).musics

    if interleave:
        tracks_by_artist = PrettyDefaultDict(list)
        for track in tracks:
            tracks_by_artist[track.artist].append(track)
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
            table.add_row(str(t.number), t.title, t.artist, t.album)
        MusicbotObject.console.print(table)


@cli.command(help='Print music tags')
@folders_argument
@extensions_option
@beartype
def tags(folders: Tuple[Path, ...], extensions: Tuple[str, ...]) -> None:
    musics = Folders(folders=folders, extensions=extensions).musics
    for music in musics:
        logger.info(music.handle.tags.keys())
        print(music.as_dict())


@cli.command(help='Convert all files in folders to mp3')
@destination_argument
@folders_argument
@concurrency_options
@dry_option
@flat_option
@beartype
def flac2mp3(folders: Tuple[Path, ...], destination: Path, concurrency: int, flat: bool) -> None:
    flac_musics = Folders(folders=folders, extensions=['flac']).musics
    if not flac_musics:
        logger.warning(f"No flac files detected in {folders}")
        return

    def convert(music: File) -> None:
        try:
            music.to_mp3(flat=flat, destination=destination)
        except MusicbotError as e:
            logger.error(e)
        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"{music} : unable to convert to mp3 : {e}")

    MusicbotObject.parallel(convert, flac_musics, concurrency=concurrency)


@cli.command(aliases=['consistency'], help='Check music files consistency')
@folders_argument
@dry_option
@checks_and_fix_options
@extensions_option
@beartype
def inconsistencies(folders: Tuple[Path, ...], extensions: Tuple[str, ...], fix: bool, checks: Tuple[str, ...]) -> None:
    musics = Folders(folders=folders, extensions=extensions).musics
    table = Table("Path", "Inconsistencies")
    for m in musics:
        try:
            if fix:
                m.fix(checks=checks)
            if m.inconsistencies.intersection(set(checks)):
                table.add_row(str(m.path), ', '.join(m.inconsistencies))
        except (OSError, mutagen.MutagenError):
            table.add_row(m.path, "could not open file")
    MusicbotObject.console.print(table)


@cli.command(help='Add keywords to music')
@dry_option
@folders_argument
@keywords_argument
@extensions_option
@beartype
def add_keywords(folders: Tuple[Path, ...], extensions: Tuple[str, ...], keywords: List[str]) -> None:
    musics = Folders(folders=folders, extensions=extensions).musics
    for music in musics:
        music.add_keywords(keywords)


@cli.command(help='Delete keywords to music')
@dry_option
@folders_argument
@keywords_argument
@extensions_option
@beartype
def delete_keywords(folders: Tuple[Path, ...], extensions: Tuple[str, ...], keywords: List[str]) -> None:
    musics = Folders(folders=folders, extensions=extensions).musics
    for music in musics:
        music.delete_keywords(keywords)
