import logging
import json
import click
import mutagen  # type: ignore
from prettytable import PrettyTable  # type: ignore
from click_skeleton import AdvancedGroup, add_options

from musicbot import helpers
from musicbot.exceptions import MusicbotError
from musicbot.config import config
from musicbot.music.file import File, flat_option, folder_option, checks_options, supported_formats
from musicbot.music.helpers import find_files

logger = logging.getLogger(__name__)


@click.group('folder', help='Manage folders', cls=AdvancedGroup)
def cli():
    pass


@cli.command(help='Just list music files')
@add_options(helpers.folders_argument)
def find(folders):
    files = find_files(folders, supported_formats)
    for f in files:
        print(f[1])


@cli.command(help='List tracks')
@add_options(
    helpers.folders_argument,
    helpers.output_option,
)
def tracks(folders, output):
    tracks = helpers.genfiles(folders)
    if output == 'json':
        tracks_dict = [{'title': t.title, 'artist': t.artist, 'album': t.album} for t in tracks]
        print(json.dumps(tracks_dict))
    elif output == 'table':
        pt = PrettyTable()
        pt.field_names = ["Track", "Title", "Artist", "Album"]
        for t in tracks:
            pt.add_row([t.number, t.title, t.artist, t.album])
        print(pt)
    else:
        raise NotImplementedError


@cli.command(help='Convert all files in folders to mp3')
@add_options(
    folder_option,
    helpers.folders_argument,
    helpers.concurrency_options,
    helpers.dry_option,
    flat_option,
)
def flac2mp3(folders, folder, concurrency, flat, dry):
    flac_files = list(find_files(folders, ['flac']))
    if not flac_files:
        logger.warning(f"No flac files detected in {folders}")
        return

    def convert(flac_tuple):
        try:
            flac_path = flac_tuple[1]
            f = File(flac_path)
            f.to_mp3(folder=folder, dry=dry, flat=flat)
        except MusicbotError as e:
            logger.error(e)
        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"{flac_path} : unable to convert to mp3 : {e}")

    config.parallel(convert, flac_files)


@cli.command(aliases=['consistency'], help='Check music files consistency')
@add_options(
    helpers.folders_argument,
    helpers.dry_option,
    checks_options,
)
def inconsistencies(folders, fix, **kwargs):
    musics = helpers.genfiles(folders)
    pt = PrettyTable()
    pt.field_names = ["Folder", "Path", "Inconsistencies"]
    for m in musics:
        try:
            if fix:
                m.fix(**kwargs)
            if m.inconsistencies:
                pt.add_row([m.folder, m.path, ', '.join(m.inconsistencies)])
        except (OSError, mutagen.MutagenError):
            pt.add_row([m.folder, m.path, "could not open file"])
    print(pt)
