import logging
import os
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


checks = ['no-title', 'bad-comment', 'invalid-artist', 'no-genre', 'no-album', 'no-artist', 'no-rating', 'invalid-track-number']
@cli.command(help='''Check music files consistency''')
@click.option('--checks', help=f'Consistency tests', multiple=True, default=checks, show_default=True, type=click.Choice(['no-title', 'invalid-title', 'bad-comment', 'invalid-artist', 'no-genre', 'no-album', 'no-artist', 'no-rating', 'invalid-track-number']))
@helpers.add_options(helpers.folders_argument)
def check_consistency(folders, checks):
    if not checks:
        logger.warning("Nothing to check")
        return

    musics = helpers.genfiles(folders)
    pt = PrettyTable()
    pt.field_names = ["Path", "Inconsistencies"]
    for m in musics:
        try:
            inconsistencies = []
            if 'invalid-comment' in checks:
                if m.path.endswith('.flac'):
                    if m.comment and not m.description:
                        inconsistencies.append(f'invalid-comment comment {m.comment} used in flac instead of description')
                if m.path.endswith('.mp3'):
                    if m.description and not m.comment:
                        inconsistencies.append(f'invalid-comment description {m.description} used in mp3 instead of comment')
            if 'no-title' in checks:
                if not m.title:
                    inconsistencies.append("no-title")
            if 'invalid-title' in checks:
                filename = os.path.basename(m.path)
                if filename != f"{str(m.number).zfill(2)} - {m.title}.mp3" or filename != f"{str(m.number).zfill(2)} - {m.title}.flac":
                    inconsistencies.append(f"invalid-title, '{filename}' should start by '{str(m.number).zfill(2)} - {m.title}'")
            if 'invalid-artist' in checks:
                if m.artist not in m.path:
                    inconsistencies.append(f"invalid-artist : {m.artist} is not in path")
            if 'no-genre' in checks:
                if m.genre == '':
                    inconsistencies.append("no-genre")
            if 'no-album' in checks:
                if m.album == '':
                    inconsistencies.append("no-album")
            if 'no-artist' in checks:
                if m.artist == '':
                    inconsistencies.append("no-artist")
            if 'no-rating' in checks:
                if m.rating == 0.0:
                    inconsistencies.append("no-rating")
            if 'invalid-track-number' in checks:
                if m.number == -1:
                    inconsistencies.append("invalid-track-number")
            if inconsistencies:
                pt.add_row([m.path, ', '.join(inconsistencies)])
        except OSError:
            pt.add_row([m.path, "Could not open file"])
    print(pt)
