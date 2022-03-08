import logging
from pathlib import Path

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
    path_argument,
    paths_arguments,
)
from musicbot.cli.folders import destination_argument
from musicbot.cli.music_filter import link_options
from musicbot.cli.musicdb import musicdb_options
from musicbot.cli.options import dry_option
from musicbot.file import File
from musicbot.musicdb import MusicDb
from musicbot.object import MusicbotObject

logger = logging.getLogger(__name__)


@click.group('music', help='Music file', cls=AdvancedGroup, aliases=['file'])
@beartype
def cli() -> None:
    pass


@cli.command(help='Insert music to DB', aliases=['upsert', 'scan'])
@path_argument
@musicdb_options
@link_options
@beartype
def insert(
    path: Path,
    musicdb: MusicDb,
    http: bool,
    sftp: bool,
    youtube: bool,
    spotify: bool,
    local: bool,
) -> None:
    music = File(path=path)
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


@cli.command(help='Print music tags', aliases=['tag'])
@path_argument
@beartype
def tags(path: Path) -> None:
    f = File(path=path)
    logger.info(f.handle.tags.keys())
    MusicbotObject.print_json(f.to_dict())


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
        music = File(path=path)
        if title is not None:
            music.title = title
        if artist is not None:
            music.artist = artist
        if album is not None:
            music.album = album
        if genre is not None:
            music.genre = genre
        if keywords is not None:
            music.keywords = set(keywords)
        if rating is not None:
            music.rating = rating
        if track is not None:
            music.track = track
        music.save()


@cli.command(help='Add keywords to music')
@dry_option
@path_argument
@keywords_argument
@beartype
def add_keywords(path: Path, keywords: list[str]) -> None:
    f = File(path=path)
    f.add_keywords(set(keywords))


@cli.command(help='Delete keywords to music', aliases=['remove-keywords'])
@dry_option
@path_argument
@keywords_argument
@beartype
def delete_keywords(path: Path, keywords: list[str]) -> None:
    f = File(path=path)
    f.delete_keywords(set(keywords))
