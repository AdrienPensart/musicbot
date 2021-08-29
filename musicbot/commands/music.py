from typing import List
import logging
from prettytable import PrettyTable  # type: ignore
from mutagen import MutagenError  # type: ignore
from click_skeleton import AdvancedGroup
import click
from musicbot.music.file import File
from musicbot.cli.options import dry_option
from musicbot.cli.file import (
    keywords_argument,
    path_argument,
    folder_option,
    file_options,
    checks_and_fix_options,
    acoustid_api_key_option,
)

logger = logging.getLogger(__name__)


@click.group('music', help='Music file', cls=AdvancedGroup, aliases=['file'])
def cli():
    pass


@cli.command(help='Convert flac music to mp3')
@path_argument
@folder_option
@dry_option
def flac2mp3(path: str, folder: str):
    f = File(path)
    f.to_mp3(folder)


@cli.command(help='Print music fingerprint')
@path_argument
@acoustid_api_key_option
def fingerprint(path: str, acoustid_api_key: str):
    f = File(path)
    print(f.fingerprint(acoustid_api_key))


@cli.command(help='Print music tags')
@path_argument
def tags(path):
    f = File(path)
    logger.info(f.handle.tags.keys())
    print(f.as_dict())


@cli.command(aliases=['consistency'], help='Check music consistency')
@folder_option
@path_argument
@dry_option
@checks_and_fix_options
def inconsistencies(path: str, folder: str, fix: bool, **kwargs):
    m = File(path, folder)
    pt = PrettyTable(["Folder", "Path", "Inconsistencies"])
    try:
        if fix:
            m.fix(**kwargs)
        if m.inconsistencies:
            pt.add_row([m.folder, m.path, ', '.join(m.inconsistencies)])
    except (OSError, MutagenError):
        pt.add_row([m.folder, m.path, "could not open file"])
    print(pt)


@cli.command(help='Set music title')
@path_argument
@dry_option
@file_options
def set_tags(path: str, title: str, artist: str, album: str, genre: str, keywords: List[str], rating: float, number: int):
    f = File(path)
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
def add_keywords(path: str, keywords: List[str]):
    f = File(path)
    f.add_keywords(keywords)


@cli.command(help='Delete keywords to music', aliases=['remove-keywords'])
@dry_option
@path_argument
@keywords_argument
def delete_keywords(path: str, keywords: List[str]):
    f = File(path)
    f.delete_keywords(keywords)
