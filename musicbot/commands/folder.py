import logging
import json
import click
from prettytable import PrettyTable
from musicbot import helpers, lib
from musicbot.config import config

logger = logging.getLogger(__name__)


@click.group(help='Manage folders', cls=helpers.GroupWithHelp)
def cli():
    pass


@cli.command(help='List tracks')
@helpers.add_options(helpers.folders_argument + helpers.output_option)
def tracks(folders, output):
    tracks = helpers.genfiles(folders)
    if output == 'json':
        tracks_dict = [{'title': t.title, 'artist': t.artist, 'album': t.album} for t in tracks]
        print(json.dumps(tracks_dict))
    elif output == 'table':
        pt = PrettyTable()
        pt.field_names = ["Title", "Artist", "Album"]
        for t in tracks:
            pt.add_row([t.title, t.artist, t.album])
        print(pt)
    else:
        raise NotImplementedError


@cli.command(help='Convert all files in folders to mp3')
@helpers.add_options(helpers.folders_argument + helpers.concurrency_options + helpers.dry_option)
def flac2mp3(folders, concurrency, dry):
    import concurrent.futures as cf
    from pydub import AudioSegment
    flac_files = list(lib.find_files(folders, ['flac']))

    pbar = None
    if not config.quiet:
        pbar = click.progressbar(length=len(flac_files), label='Converting musics')

    def convert(flac_path):
        logger.debug('Converting %s', flac_path)
        flac_audio = AudioSegment.from_file(flac_path, "flac")
        mp3_path = flac_path.replace('.flac', '.mp3')
        if not dry:
            flac_audio.export(mp3_path, format="mp3")
        else:
            logger.info("[DRY-RUN] Exporting from %s to %s", flac_path, mp3_path)
        if pbar:
            pbar.update(1)
    # Permit CTRL+C to work as intended
    # import atexit
    # from concurrent.futures.thread import _python_exit
    # atexit.unregister(_python_exit)  # pylint: disable=protected-access
    with cf.ThreadPoolExecutor(max_workers=concurrency) as executor:
        executor.shutdown = lambda wait: None
        futures = [executor.submit(convert, flac_path) for flac_path in flac_files]
        cf.wait(futures)
