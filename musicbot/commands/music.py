import logging
import click
from prettytable import PrettyTable
from mutagen import MutagenError
from click_skeleton import AdvancedGroup, add_options

from musicbot import helpers
from musicbot.music.file import File, path_argument, folder_option, options, checks_options
from musicbot.music.fingerprint import acoustid_api_key_option

logger = logging.getLogger(__name__)


@click.group(help='Music file', cls=AdvancedGroup)
def cli():
    pass


@cli.command(help='Convert flac music to mp3')
@add_options(
    path_argument +
    folder_option +
    helpers.dry_option
)
def flac2mp3(path, folder, dry):
    f = File(path)
    f.to_mp3(folder, dry)


@cli.command(help='Print music fingerprint')
@add_options(
    path_argument +
    acoustid_api_key_option
)
def fingerprint(path, acoustid_api_key):
    f = File(path)
    print(f.fingerprint(acoustid_api_key))


@cli.command(help='Print music tags')
@add_options(
    path_argument
)
def tags(path):
    f = File(path)
    logger.info(f.handle.tags.keys())
    print(f.ordered_dict())


@cli.command(aliases=['consistency'], help='Check music consistency')
@add_options(
    folder_option +
    path_argument +
    helpers.dry_option +
    checks_options
)
def inconsistencies(path, folder, fix, **kwargs):
    m = File(path, folder)
    pt = PrettyTable()
    pt.field_names = ["Folder", "Path", "Inconsistencies"]
    try:
        if fix:
            m.fix(**kwargs)
        if m.inconsistencies:
            pt.add_row([m.folder, m.path, ', '.join(m.inconsistencies)])
    except (OSError, MutagenError):
        pt.add_row([m.folder, m.path, "could not open file"])
    print(pt)


@cli.command(help='Set music title')
@add_options(
    path_argument +
    options
)
def set_tags(path, title, artist, album, genre, keywords, rating, number):
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
