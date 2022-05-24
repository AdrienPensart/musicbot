import logging
from pathlib import Path

import click
from attr import asdict
from beartype import beartype
from click_skeleton import AdvancedGroup
from mutagen import MutagenError  # type: ignore
from rich.table import Table

from musicbot.cli.file import (
    acoustid_api_key_option,
    checks_and_fix_options,
    file_options,
    keywords_arguments,
    music_argument,
    paths_arguments
)
from musicbot.cli.folders import destination_argument
from musicbot.cli.options import dry_option
from musicbot.file import File
from musicbot.object import MusicbotObject

logger = logging.getLogger(__name__)


@click.group('music', help='Music file', cls=AdvancedGroup, aliases=['file'])
@beartype
def cli() -> None:
    pass


@cli.command(help='Convert flac music to mp3', aliases=['flac-to-mp3'])
@music_argument
@destination_argument
@beartype
def flac2mp3(
    music: File,
    destination: Path
) -> None:
    if not music.to_mp3(destination):
        MusicbotObject.err(f"{music} : unable to convert to MP3")


@cli.command(help='Print music fingerprint')
@music_argument
@acoustid_api_key_option
@beartype
def fingerprint(
    music: File,
    acoustid_api_key: str
) -> None:
    print(music.fingerprint(acoustid_api_key))


@cli.command(help='Print music tags', aliases=['tag'])
@music_argument
@beartype
def tags(music: File) -> None:
    logger.info(music.handle.tags.keys())
    MusicbotObject.print_json(asdict(music.to_music()))


@cli.command(aliases=['consistency'], help='Check music consistency')
@music_argument
@checks_and_fix_options
@beartype
def inconsistencies(music: File, fix: bool, checks: list[str]) -> None:
    table = Table("Path", "Inconsistencies")
    try:
        if fix and not music.fix(checks=checks):
            MusicbotObject.err(f"{music} : unable to fix inconsistencies")

        if music.inconsistencies:
            table.add_row(str(music.path), ', '.join(music.inconsistencies))
    except (OSError, MutagenError):
        table.add_row(str(music.path), "could not open file")
    MusicbotObject.console.print(table)


@cli.command(help='Set music title', aliases=['set-tag'])
@paths_arguments
@dry_option
@file_options
@beartype
def set_tags(
    paths: list[Path],
    title: str | None = None,
    artist: str | None = None,
    album: str | None = None,
    genre: str | None = None,
    keywords: list[str] | None = None,
    rating: float | None = None,
    track: int | None = None,
) -> None:
    for path in paths:
        file = File.from_path(path=path)
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
@music_argument
@keywords_arguments
@dry_option
@beartype
def add_keywords(music: File, keywords: set[str]) -> None:
    if not music.add_keywords(keywords):
        MusicbotObject.err(f"{music} : unable to add keywords")


@cli.command(help='Delete keywords to music', aliases=['remove-keywords'])
@music_argument
@keywords_arguments
@dry_option
@beartype
def delete_keywords(music: File, keywords: set[str]) -> None:
    if not music.delete_keywords(keywords):
        MusicbotObject.err(f"{music} : unable to delete keywords")
