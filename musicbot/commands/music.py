import logging
import click
from pydub import AudioSegment
from musicbot import helpers
from musicbot.music.file import File, options, checks_options
from musicbot.music.fingerprint import acoustid_api_key_option

logger = logging.getLogger(__name__)


@click.group(help='Music file', cls=helpers.GroupWithHelp)
def cli():
    pass


@cli.command(help='Convert flac music to mp3')
@click.argument('path')
def flac2mp3(path):
    if not path.endswith('.flac'):
        logger.error(f"{path} is not a flac file")
        return
    mp3_path = path.replace('.flac', '.mp3')
    flac_audio = AudioSegment.from_file(path, "flac")
    flac_audio.export(mp3_path, format="mp3")


@cli.command(help='Print music fingerprint')
@click.argument('path')
@helpers.add_options(acoustid_api_key_option)
def fingerprint(path, acoustid_api_key):
    f = File(path)
    print(f.fingerprint(acoustid_api_key))


@cli.command(help='Print music tags')
@click.argument('path')
def tags(path):
    f = File(path)
    logger.info(f.handle.tags.keys())
    print(f.ordered_dict())


@cli.command(help='Check music consistency')
@click.argument('path')
@helpers.add_options(checks_options)
def check_consistency(path, **kwargs):
    f = File(path)
    logger.info(f.handle.tags.keys())
    print(f.check_consistency(**kwargs))


@cli.command(help='Set music title')
@click.argument('path')
@helpers.add_options(options)
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
