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
    keywords_arguments,
    music_argument,
    paths_arguments
)
from musicbot.cli.folders import destination_argument
from musicbot.cli.link_options import link_options_options
from musicbot.cli.musicdb import musicdb_options
from musicbot.cli.options import dry_option
from musicbot.file import File
from musicbot.link_options import LinkOptions
from musicbot.musicdb import MusicDb
from musicbot.object import MusicbotObject

logger = logging.getLogger(__name__)


@click.group('music', help='Music file', cls=AdvancedGroup, aliases=['file'])
@beartype
def cli() -> None:
    pass


@cli.command(help='Insert music to DB', aliases=['upsert', 'scan'])
@music_argument
@musicdb_options
@link_options_options
@beartype
def insert(
    music: File,
    musicdb: MusicDb,
    link_options: LinkOptions,
) -> None:
    if 'no-title' in music.inconsistencies or 'no-artist' in music.inconsistencies or 'no-album' in music.inconsistencies:
        MusicbotObject.warn(f"{music} : missing mandatory fields title/album/artist : {music.inconsistencies}")
        return

    musicdb.upsert_music(
        music,
        link_options=link_options
    )


@cli.command(help='Convert flac music to mp3')
@music_argument
@destination_argument
@dry_option
@beartype
def flac2mp3(
    music: File,
    destination: Path
) -> None:
    music.to_mp3(destination)


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
    MusicbotObject.print_json(music.to_dict())


@cli.command(aliases=['consistency'], help='Check music consistency')
@music_argument
@dry_option
@checks_and_fix_options
@beartype
def inconsistencies(music: File, fix: bool, checks: list[str]) -> None:
    table = Table("Path", "Inconsistencies")
    try:
        if fix:
            music.fix(checks=checks)
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
        music = File.from_path(path=path)
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
@music_argument
@keywords_arguments
@beartype
def add_keywords(music: File, keywords: set[str]) -> None:
    music.add_keywords(keywords)


@cli.command(help='Delete keywords to music', aliases=['remove-keywords'])
@dry_option
@music_argument
@keywords_arguments
@beartype
def delete_keywords(music: File, keywords: set[str]) -> None:
    music.delete_keywords(keywords)
