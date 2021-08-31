from typing import List
from pathlib import Path
import logging
import json
import random
import itertools
import click
import mutagen  # type: ignore
from prettytable import PrettyTable  # type: ignore
from click_skeleton import AdvancedGroup
from click_skeleton.helpers import PrettyDefaultDict
from musicbot.cli.options import output_option, concurrency_options, dry_option
from musicbot.cli.music_filter import ordering_options
from musicbot.cli.file import keywords_argument, flat_option, checks_and_fix_options
from musicbot.cli.folders import destination_argument, folder_argument, folders_argument

from musicbot.exceptions import MusicbotError
from musicbot.object import MusicbotObject
from musicbot.music.file import File, supported_formats
from musicbot.music.folders import Folders

logger = logging.getLogger(__name__)


@click.group('folder', help='Manage folders', cls=AdvancedGroup)
def cli():
    pass


@cli.command(help='Just list music files')
@folders_argument
def find(folders: List[Path]):
    files = Folders(folders).supported_files(supported_formats)
    for file in files:
        print(file)


@cli.command(help='Generate a playlist', aliases=['tracks'])
@folders_argument
@output_option
@ordering_options
def playlist(folders: List[Path], output: str, shuffle: bool, interleave: bool):
    tracks = Folders(folders).musics()

    if interleave:
        tracks_by_artist = PrettyDefaultDict(list)
        for track in tracks:
            tracks_by_artist[track.artist].append(track)
        tracks = [
            track
            for track in itertools.chain(*itertools.zip_longest(*tracks_by_artist.values()))
            if track is not None
        ]

    if shuffle:
        random.shuffle(tracks)

    if output == 'm3u':
        p = '#EXTM3U\n'
        p += '\n'.join([track.path for track in tracks])
        print(p)
        return

    if output == 'json':
        tracks_dict = [{'title': t.title, 'artist': t.artist, 'album': t.album} for t in tracks]
        print(json.dumps(tracks_dict))
        return

    if output == 'table':
        pt = PrettyTable(["Track", "Title", "Artist", "Album"])
        for t in tracks:
            pt.add_row([t.number, t.title, t.artist, t.album])
        print(pt)


@cli.command(help='Print music tags')
@folders_argument
def tags(folders: List[Path]):
    musics = Folders(folders).musics()
    for music in musics:
        logger.info(music.handle.tags.keys())
        print(music.as_dict())


@cli.command(help='Convert all files in folders to mp3')
@destination_argument
@folders_argument
@concurrency_options
@dry_option
@flat_option
def flac2mp3(folders: List[Path], destination: Path, concurrency: int, flat: bool):
    flac_files = Folders(folders).supported_files(['flac'])
    if not flac_files:
        logger.warning(f"No flac files detected in {folders}")
        return

    def convert(path):
        try:
            f = File(path=path)
            f.to_mp3(flat=flat, destination=destination)
        except MusicbotError as e:
            logger.error(e)
        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"{path} : unable to convert to mp3 : {e}")

    MusicbotObject.parallel(convert, flac_files, concurrency=concurrency)


@cli.command(aliases=['consistency'], help='Check music files consistency')
@folders_argument
@dry_option
@checks_and_fix_options
def inconsistencies(folders: List[Path], fix: bool, checks: List[str]):
    musics = Folders(folders).musics()
    pt = PrettyTable(["Path", "Inconsistencies"])
    for m in musics:
        try:
            if fix:
                m.fix(checks=checks)
            if set(m.inconsistencies).intersection(set(checks)):
                pt.add_row([m.path, ', '.join(m.inconsistencies)])
        except (OSError, mutagen.MutagenError):
            pt.add_row([m.path, "could not open file"])
    pt.align["Path"] = "l"
    print(pt)


@cli.command(help='Add keywords to music')
@dry_option
@folder_argument
@keywords_argument
def add_keywords(folder: Path, keywords: List[str]):
    musics = Folders([folder]).musics()
    for music in musics:
        music.add_keywords(keywords)


@cli.command(help='Delete keywords to music')
@dry_option
@folder_argument
@keywords_argument
def delete_keywords(folder: Path, keywords: List[str]):
    musics = Folders([folder]).musics()
    for music in musics:
        music.delete_keywords(keywords)
