from typing import List
from pathlib import Path
import logging
from prettytable import PrettyTable  # type: ignore
from mutagen import MutagenError  # type: ignore
from click_skeleton import AdvancedGroup
import click
from musicbot.music.file import File
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
from musicbot.user import User

logger = logging.getLogger(__name__)


@click.group('music', help='Music file', cls=AdvancedGroup, aliases=['file'])
def cli():
    pass


@cli.command(help='Insert music in DB')
@path_argument
@user_options
@dry_option
@link_options
def insert(path: Path, user: User, **link_options):
    f = File(path=path)
    user.insert(f, **link_options)


@cli.command(help='Convert flac music to mp3')
@path_argument
@destination_argument
@dry_option
def flac2mp3(path: Path, destination: Path):
    f = File(path=path)
    f.to_mp3(destination)


@cli.command(help='Print music fingerprint')
@path_argument
@acoustid_api_key_option
def fingerprint(path: Path, acoustid_api_key: str):
    f = File(path=path)
    print(f.fingerprint(acoustid_api_key))


@cli.command(help='Print music tags')
@path_argument
def tags(path: Path):
    f = File(path=path)
    logger.info(f.handle.tags.keys())
    print(f.as_dict())


@cli.command(aliases=['consistency'], help='Check music consistency')
@path_argument
@dry_option
@checks_and_fix_options
def inconsistencies(path: Path, fix: bool, **kwargs):
    m = File(path=path)
    pt = PrettyTable(["Path", "Inconsistencies"])
    try:
        if fix:
            m.fix(**kwargs)
        if m.inconsistencies:
            pt.add_row([m.path, ', '.join(m.inconsistencies)])
    except (OSError, MutagenError):
        pt.add_row([m.path, "could not open file"])
    print(pt)


@cli.command(help='Set music title')
@path_argument
@dry_option
@file_options
def set_tags(path: Path, title: str, artist: str, album: str, genre: str, keywords: List[str], rating: float, number: int):
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
def add_keywords(path: Path, keywords: List[str]):
    f = File(path=path)
    f.add_keywords(keywords)


@cli.command(help='Delete keywords to music', aliases=['remove-keywords'])
@dry_option
@path_argument
@keywords_argument
def delete_keywords(path: Path, keywords: List[str]):
    f = File(path=path)
    f.delete_keywords(keywords)
