import logging
import json
import concurrent.futures as cf
import click
from pydub import AudioSegment
from prettytable import PrettyTable
from musicbot import helpers, lib
from musicbot.config import config
from musicbot.music.file import checks_options

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
    flac_files = list(lib.find_files(folders, ['flac']))
    if not flac_files:
        logger.warning(f"No flac files detected in {folders}")
        return

    with config.tqdm(total=len(flac_files), leave=True, desc='Converting musics') as pbar:
        with cf.ThreadPoolExecutor(max_workers=concurrency) as executor:
            def convert(flac_path):
                mp3_path = flac_path.replace('.flac', '.mp3')
                if not dry:
                    logger.info(f"Converting {flac_path} to {mp3_path}")
                    flac_audio = AudioSegment.from_file(flac_path, "flac")
                    flac_audio.export(mp3_path, format="mp3")
                else:
                    logger.info(f"[DRY-RUN] Exporting from {flac_path} to {mp3_path}")
                pbar.update(1)
            executor.shutdown = lambda wait: None
            futures = [executor.submit(convert, flac_path[1]) for flac_path in flac_files]
            cf.wait(futures)


@cli.command(help='Check music files consistency')
@helpers.add_options(helpers.folders_argument + checks_options)
def check_consistency(folders, checks, fix):
    if not checks:
        logger.warning("Nothing to check")
        return

    musics = helpers.genfiles(folders)
    pt = PrettyTable()
    pt.field_names = ["Path", "Inconsistencies"]
    for m in musics:
        try:
            inconsistencies = m.check_consistency(checks, fix)
            if inconsistencies:
                pt.add_row([m.path, ', '.join(inconsistencies)])
        except OSError:
            pt.add_row([m.path, "Could not open file"])
    print(pt)
