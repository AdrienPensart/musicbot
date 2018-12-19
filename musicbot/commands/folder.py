import click
import os
import csv
import logging
import click_spinner
from tqdm import tqdm
from musicbot import helpers, lib, user
from musicbot.music import mfilter
from musicbot.config import config

logger = logging.getLogger(__name__)


@click.group(cls=helpers.GroupWithHelp)
@click.pass_context
@helpers.add_options(user.auth_options)
def cli(ctx, **kwargs):
    '''Folder management'''
    ctx.obj.u = lambda: user.User.new(**kwargs)
    lib.raise_limits()


@cli.command()
@click.pass_context
def list(ctx):
    '''List folders'''
    print(ctx.obj.u().folders)


@cli.command()
@click.argument('folders', nargs=-1)
@click.pass_context
def scan(ctx, folders):
    '''(re)Load musics'''
    u = ctx.obj.u()
    if not len(folders):
        folders = u.folders

    print('Scanning folder')
    with click_spinner.spinner(disable=config.quiet):
        files = helpers.genfiles(folders)

    print('Inserting musics')
    with click_spinner.spinner(disable=config.quiet):
        u.bulk_insert(files)


@cli.command()
@click.argument('folders', nargs=-1)
@click.pass_context
def find(ctx, folders):
    '''Just list music files'''
    u = ctx.obj.u()
    if not len(folders):
        folders = u.folders

    files = lib.find_files(folders)
    for f in files:
        print(f[1])


@cli.command('csv')
@click.argument('path', type=click.File('w'), default='-')
@click.pass_context
def _csv(ctx, path):
    '''Export music files to csv file'''
    u = ctx.obj.u()
    folders = u.folders

    logger.info('Scanning folders', folders)
    files = helpers.genfiles(folders)

    musicwriter = csv.writer(path, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    for f in files:
        musicwriter.writerow(f.ordered_dict().values())


@cli.command()
@click.pass_context
def watch(ctx):
    '''Watch files changes in folders'''
    ctx.obj.u().watch()


@cli.command()
@click.argument('folders', nargs=-1)
@helpers.add_options(helpers.concurrency_options)
def flac2mp3(folders, concurrency):
    '''Convert all files in folders to mp3'''
    import atexit
    import concurrent.futures as cf
    from pydub import AudioSegment
    files = lib.find_files(folders)
    flac_files = [f[1] for f in files if f[1].endswith('.flac')]

    pbar = None
    if not config.quiet:
        pbar = click.progressbar(length=len(flac_files), label='Converting musics')

    def convert(flac_path):
        logger.debug('Converting %s', flac_path)
        flac_audio = AudioSegment.from_file(flac_path, "flac")
        mp3_path = flac_path.replace('.flac', '.mp3')
        flac_audio.export(mp3_path, format="mp3")
        if pbar:
            pbar.update(1)
    # Permit CTRL+C to work as intended
    atexit.unregister(cf.thread._python_exit)  # pylint: disable=protected-access
    with cf.ThreadPoolExecutor(max_workers=concurrency) as executor:
        executor.shutdown = lambda wait: None
        futures = [executor.submit(convert, flac_path) for flac_path in flac_files]
        cf.wait(futures)


@cli.command()
@helpers.add_options(mfilter.options)
@click.argument('destination')
@click.pass_context
def sync(ctx, destination, **kwargs):
    '''Copy selected musics with filters to destination folder'''
    logger.info('Destination: %s', destination)
    mf = mfilter.Filter(**kwargs)
    musics = ctx.obj.u().do_filter(mf)

    files = lib.all_files(destination)
    destinations = {f[len(destination) + 1:]: f for f in files}
    sources = {m['path'][len(m['folder']) + 1:]: m['path'] for m in musics}
    to_delete = set(destinations.keys()) - set(sources.keys())
    if to_delete:
        with tqdm(total=len(to_delete), desc="Deleting music", disable=config.quiet) as pbar:
            for d in to_delete:
                if not config.dry:
                    try:
                        logger.info("Deleting %s", destinations[d])
                        os.remove(destinations[d])
                    except Exception as e:
                        logger.error(e)
                else:
                    logger.info("[DRY-RUN] False Deleting %s", destinations[d])
                pbar.update(1)
    to_copy = set(sources.keys()) - set(destinations.keys())
    if to_copy:
        with tqdm(total=len(to_copy), desc="Copying music", disable=config.quiet) as pbar:
            from shutil import copyfile
            for c in sorted(to_copy):
                final_destination = os.path.join(destination, c)
                if not config.dry:
                    logger.info("Copying %s to %s", sources[c], final_destination)
                    os.makedirs(os.path.dirname(final_destination), exist_ok=True)
                    copyfile(sources[c], final_destination)
                else:
                    logger.info("[DRY-RUN] False Copying %s to %s", sources[c], final_destination)
                pbar.update(1)

    import shutil
    for d in lib.empty_dirs(destination):
        if not config.dry:
            shutil.rmtree(d)
        logger.info("[DRY-RUN] Removing empty dir %s", d)


@cli.command()
@click.pass_context
@click.argument('folders', nargs=-1)
def consistency(ctx, folders):
    '''Check music files consistency'''
    if not len(folders):
        folders = ctx.obj.u().folders

    musics = helpers.genfiles(folders)
    report = []
    for m in musics:
        try:
            if m.path.endswith('.flac'):
                if m.comment and not m.description:
                    report.append('Comment (' + m.comment + ') used in flac: ' + m.path)
            if m.path.endswith('.mp3'):
                if m.description and not m.comment:
                    report.append('Description (' + m.description + ') used in mp3 : ' + m.path)
            if not m.title:
                report.append("No title  : '" + m.title + "' on " + m.path)
            filename = os.path.basename(m.path)
            if filename == "{} - {}.mp3".format(str(m.number).zfill(2), m.title):
                continue
            if filename == "{} - {}.flac".format(str(m.number).zfill(2), m.title):
                continue
            report.append("Invalid title format, '{}' should start by '{}'".
                          format(filename, '{} - {}'.format(str(m.number).zfill(2), m.title)))
            if m.artist not in m.path:
                report.append("Artist invalid : " + m.artist + " is not in " + m.path)
            if m.genre == '':
                report.append("No genre : " + m.path)
            if m.album == '':
                report.append("No album : " + m.path)
            if m.artist == '':
                report.append("No artist : " + m.path)
            if m.rating == 0.0:
                report.append("No rating : " + m.path)
            if m.number == -1:
                report.append("Invalid track number : " + m.path)
        except OSError:
            report.append("Could not open file : " + m.path)
    print(report)
