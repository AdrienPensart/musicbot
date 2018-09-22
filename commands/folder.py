import click
import os
import asyncio
import logging
import atexit
import concurrent.futures as cf
from pydub import AudioSegment
from tqdm import tqdm
from lib import helpers, lib, collection, database, mfilter
from lib.config import config
from lib.helpers import watcher, fullscan
from lib.lib import empty_dirs

logger = logging.getLogger(__name__)


@click.group(cls=helpers.GroupWithHelp)
@helpers.add_options(database.options)
@click.pass_context
def cli(ctx, **kwargs):
    '''Folder scanning'''
    lib.raise_limits()
    ctx.obj.db = collection.Collection(**kwargs)


@cli.command()
@helpers.coro
@click.argument('folders', nargs=-1)
@click.pass_context
async def new(ctx, folders):
    '''Add a new folder in database'''
    tasks = [asyncio.ensure_future(ctx.obj.db.new_folder(f)) for f in folders]
    await asyncio.gather(*tasks)


@cli.command('list')
@helpers.coro
@click.pass_context
async def ls(ctx):
    '''List existing folders'''
    folders = await ctx.obj.db.folders()
    for f in folders:
        print(f['name'])


@cli.command()
@helpers.coro
@click.option('--crawl', envvar='MB_CRAWL', help='Crawl youtube', is_flag=True)
@click.argument('folders', nargs=-1)
@click.pass_context
async def scan(ctx, **kwargs):
    '''Load musics files in database'''
    await fullscan(ctx.obj.db, **kwargs)


@cli.command()
@helpers.coro
@click.option('--crawl', envvar='MB_CRAWL', help='Crawl youtube', is_flag=True)
@click.pass_context
async def rescan(ctx, **kwargs):
    '''Rescan all folders registered in database'''
    await fullscan(ctx.obj.db, **kwargs)


@cli.command()
@helpers.coro
@click.pass_context
async def watch(ctx):
    '''Watch files changes in folders'''
    await watcher(ctx.obj.db)


@cli.command()
@click.argument('folders', nargs=-1)
def find(folders):
    '''Only list files in selected folders'''
    files = lib.find_files(folders)
    for f in files:
        print(f[1])


@cli.command()
@click.argument('folders', nargs=-1)
@helpers.add_options(helpers.concurrency_options)
def flac2mp3(folders, concurrency):
    '''Convert all files in folders to mp3'''
    files = lib.find_files(folders)
    flac_files = [f[1] for f in files if f[1].endswith('.flac')]
    with tqdm(desc='Converting musics', total=len(flac_files), disable=config.quiet) as pbar:
        def convert(flac_path):
            logger.debug('Converting %s', flac_path)
            flac_audio = AudioSegment.from_file(flac_path, "flac")
            mp3_path = flac_path.replace('.flac', '.mp3')
            flac_audio.export(mp3_path, format="mp3")
            pbar.update(1)
        # Permit CTRL+C to work as intended
        atexit.unregister(cf.thread._python_exit)  # pylint: disable=protected-access
        with cf.ThreadPoolExecutor(max_workers=concurrency) as executor:
            executor.shutdown = lambda wait: None
            futures = [executor.submit(convert, flac_path) for flac_path in flac_files]
            cf.wait(futures)
# from pydub import AudioSegment
# from pydub.utils import mediainfo
#
# seg = AudioSegment.from_file('original.mp3')
# seg.export('out.mp3', format='mp3', tags=mediainfo('original.mp3').get('TAG', {}))


# pylint: disable-msg=too-many-locals
@cli.command()
@helpers.coro
@helpers.add_options(mfilter.options)
@click.argument('destination')
@click.pass_context
async def sync(ctx, destination, **kwargs):
    '''Copy selected musics with filters to destination folder'''
    logger.info('Destination: %s', destination)
    ctx.obj.mf = mfilter.Filter(**kwargs)
    musics = await ctx.obj.db.musics(ctx.obj.mf)

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
    for d in empty_dirs(destination):
        if not config.dry:
            shutil.rmtree(d)
        logger.info("[DRY-RUN] Removing empty dir %s", d)
