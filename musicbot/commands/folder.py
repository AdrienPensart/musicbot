import logging
from pathlib import Path

import click
import mutagen  # type: ignore
from beartype import beartype
from click_skeleton import AdvancedGroup
from rich.table import Table

from musicbot.cli.file import (
    checks_and_fix_options,
    file_options,
    flat_option,
    keywords_arguments
)
from musicbot.cli.folders import destination_argument, folders_argument
from musicbot.cli.options import dry_option, output_option, threads_option
from musicbot.folders import Folders
from musicbot.object import MusicbotObject
from musicbot.playlist import Playlist

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


@cli.command(help='Generates a playlist', aliases=['tags', 'musics', 'tracks'])
@folders_argument
@output_option
@beartype
def playlist(
    folders: Folders,
    output: str,
) -> None:
    playlist = Playlist(musics=folders.musics)
    playlist.print(
        output=output,
    )


@cli.command(help='Convert all files in folders to mp3', aliases=['flac-to-mp3'])
@destination_argument
@folders_argument
@threads_option
@flat_option
@output_option
@beartype
def flac2mp3(
    folders: Folders,
    destination: Path,
    output: str,
    threads: int,
    flat: bool,
) -> None:
    mp3_files = folders.flac_to_mp3(
        destination=destination,
        threads=threads,
        flat=flat,
    )
    playlist = Playlist.from_files(mp3_files)
    playlist.print(
        output=output,
    )


@cli.command(aliases=['consistency'], help='Check music files consistency')
@folders_argument
@checks_and_fix_options
@beartype
def inconsistencies(
    folders: Folders,
    fix: bool,
    checks: list[str],
) -> None:
    table = Table("Path", "Inconsistencies")
    for file in folders.files:
        try:
            if fix and not file.fix(checks=frozenset(checks)):
                MusicbotObject.err(f"{file} : unable to fix inconsistencies")
                continue

            if file.inconsistencies.intersection(set(checks)):
                table.add_row(str(file.path), ', '.join(file.inconsistencies))
        except (OSError, mutagen.MutagenError):
            table.add_row(str(file.path), "could not open file")
    MusicbotObject.console.print(table)


@cli.command(help='Set music title', aliases=['set-tag'])
@folders_argument
@dry_option
@file_options
@beartype
def set_tags(
    folders: Folders,
    title: str | None = None,
    artist: str | None = None,
    album: str | None = None,
    genre: str | None = None,
    keywords: list[str] | None = None,
    rating: float | None = None,
    track: int | None = None,
) -> None:
    for file in folders.files:
        if not file.set_tags(
            title=title,
            artist=artist,
            album=album,
            genre=genre,
            keywords=keywords,
            rating=rating,
            track=track,
        ):
            MusicbotObject.err(f"{file} : unable to set tags")


@cli.command(help='Add keywords to music')
@folders_argument
@keywords_arguments
@dry_option
@beartype
def add_keywords(
    folders: Folders,
    keywords: set[str],
) -> None:
    for file in folders.files:
        if not file.add_keywords(keywords):
            MusicbotObject.err(f"{file} : unable to add keywords")


@cli.command(help='Delete keywords to music')
@folders_argument
@keywords_arguments
@dry_option
@beartype
def delete_keywords(
    folders: Folders,
    keywords: set[str],
) -> None:
    for file in folders.files:
        if not file.delete_keywords(keywords):
            MusicbotObject.err(f"{file} : unable to delete keywords")
