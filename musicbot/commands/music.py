from typing import List, Tuple
from pathlib import Path
import logging
from rich.table import Table
from mutagen import MutagenError  # type: ignore
from click_skeleton import AdvancedGroup
import click
from beartype import beartype
from musicbot.cli.options import dry_option
from musicbot.cli.folders import destination_argument
from musicbot.cli.user import user_options
from musicbot.cli.file import (
    link_options,
    keywords_argument,
    path_argument,
    file_options,
    checks_and_fix_options,
    acoustid_api_key_option,
)
from musicbot.object import MusicbotObject
from musicbot.user import User
from musicbot.music.file import File

logger = logging.getLogger(__name__)


@click.group('music', help='Music file', cls=AdvancedGroup, aliases=['file'])
@beartype
def cli() -> None:
    pass


@cli.command(help='Insert music in DB')
@path_argument
@user_options
@dry_option
@link_options
@beartype
def insert(
    path: Path,
    user: User,
    http: bool,
    sftp: bool,
    youtube: bool,
    spotify: bool,
    local: bool,
) -> None:
    f = File(path=path)
    user.insert(
        f,
        http=http,
        sftp=sftp,
        youtube=youtube,
        spotify=spotify,
        local=local,
    )


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
    print(f.as_dict())


@cli.command(aliases=['consistency'], help='Check music consistency')
@path_argument
@dry_option
@checks_and_fix_options
@beartype
def inconsistencies(path: Path, fix: bool, checks: Tuple[str, ...]) -> None:
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
def set_tags(path: Path, title: str, artist: str, album: str, genre: str, keywords: List[str], rating: float, number: int) -> None:
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
    if number:
        f.number = number
    f.save()


@cli.command(help='Add keywords to music')
@dry_option
@path_argument
@keywords_argument
@beartype
def add_keywords(path: Path, keywords: Tuple[str, ...]) -> None:
    f = File(path=path)
    f.add_keywords(keywords)


@cli.command(help='Delete keywords to music', aliases=['remove-keywords'])
@dry_option
@path_argument
@keywords_argument
@beartype
def delete_keywords(path: Path, keywords: Tuple[str, ...]) -> None:
    f = File(path=path)
    f.delete_keywords(keywords)
