import logging
from pathlib import Path
from typing import Optional

import click
from beartype import beartype
from click_skeleton import AdvancedGroup
from mutagen import MutagenError  # type: ignore
from rich.table import Table

from musicbot.cli.file import (
    acoustid_api_key_option,
    checks_and_fix_options,
    file_options,
    keywords_argument,
    path_argument
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


@cli.command(help='Convert flac music to mp3')
@path_argument
@destination_argument
@dry_option
@beartype
def flac2mp3(path: Path, destination: Path) -> None:
    f = File(path=path)
    f.to_mp3(destination)


@cli.command(help='Print music fingerprint')
@path_argument
@acoustid_api_key_option
@beartype
def fingerprint(path: Path, acoustid_api_key: str) -> None:
    f = File(path=path)
    print(f.fingerprint(acoustid_api_key))


@cli.command(help='Print music tags')
@path_argument
@beartype
def tags(path: Path) -> None:
    f = File(path=path)
    logger.info(f.handle.tags.keys())
    print(f.to_dict())


@cli.command(aliases=['consistency'], help='Check music consistency')
@path_argument
@dry_option
@checks_and_fix_options
@beartype
def inconsistencies(path: Path, fix: bool, checks: list[str]) -> None:
    m = File(path=path)
    table = Table("Path", "Inconsistencies")
    try:
        if fix:
            m.fix(checks=checks)
        if m.inconsistencies:
            table.add_row(str(m.path), ', '.join(m.inconsistencies))
    except (OSError, MutagenError):
        table.add_row(str(m.path), "could not open file")
    MusicbotObject.console.print(table)


@cli.command(help='Set music title')
@path_argument
@dry_option
@file_options
@beartype
def set_tags(
    path: Path,
    title: Optional[str],
    artist: Optional[str],
    album: Optional[str],
    genre: Optional[str],
    keywords: list[str],
    rating: Optional[float],
    track: Optional[int],
) -> None:
    f = File(path=path)
    if title:
        f.title = title
    if artist:
        f.artist = artist
    if album:
        f.album = album
    if genre:
        f.genre = genre
    if keywords:
        f.keywords = keywords
    if rating:
        f.rating = rating
    if track:
        f.track = track
    f.save()


@cli.command(help='Add keywords to music')
@dry_option
@path_argument
@keywords_argument
@beartype
def add_keywords(path: Path, keywords: list[str]) -> None:
    f = File(path=path)
    f.add_keywords(keywords)


@cli.command(help='Delete keywords to music', aliases=['remove-keywords'])
@dry_option
@path_argument
@keywords_argument
@beartype
def delete_keywords(path: Path, keywords: list[str]) -> None:
    f = File(path=path)
    f.delete_keywords(keywords)
