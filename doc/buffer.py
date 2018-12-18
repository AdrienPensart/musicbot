def check_consistency(musics, checks, no_checks):
    report = []
    for m in musics:
        try:
            if 'keywords' in checks and 'keywords' not in no_checks:
                f = file.MusicFile(m.path)
                if m.path.endswith('.flac'):
                    if f.comment and not f.description:
                        report.append('Comment (' + f.comment +
                                      ') used in flac: ' + m.path)
                if m.path.endswith('.mp3'):
                    if f.description and not f.comment:
                        report.append(
                            'Description (' +
                            f.description +
                            ') used in mp3 : ' +
                            m.path)
            if 'title' in checks and 'title' not in no_checks and not m.title:
                report.append("No title  : '" + m.title + "' on " + m.path)
            if 'strict_title' in checks and 'strict_title' not in no_checks:
                filename = os.path.basename(m.path)
                if filename == "{} - {}.mp3".format(str(m.number).zfill(2), m.title):
                    continue
                if filename == "{} - {}.flac".format(str(m.number).zfill(2), m.title):
                    continue
                report.append("Invalid title format, '{}' should start by '{}'".
                              format(filename, '{} - {}'.format(str(m.number).zfill(2), m.title)))
            if 'path' in checks and 'path' not in no_checks and m.artist not in m.path:
                report.append("Artist invalid : " +
                              m.artist + " is not in " + m.path)
            if 'genre' in checks and 'genre' not in no_checks and m.genre == '':
                report.append("No genre : " + m.path)
            if 'album' in checks and 'album' not in no_checks and m.album == '':
                report.append("No album :i " + m.path)
            if 'artist' in checks and 'artist' not in no_checks and m.artist == '':
                report.append("No artist : " + m.path)
            if 'rating' in checks and 'rating' not in no_checks and m.rating == 0.0:
                report.append("No rating : " + m.path)
            if 'number' in checks and m.number == -1:
                report.append("Invalid track number : " + m.path)
        except OSError:
            report.append("Could not open file : " + m.path)
    return report

from .config import config
from .mfilter import Filter, supported_formats
from . import youtube, spotify
@timeit
async def crawl_musics(db, mf=None, concurrency=1):
    if mf is None:
        mf = Filter(youtubes=[''])
    musics = await db.musics(mf)
    with tqdm(desc='Youtube musics', total=len(musics), disable=config.quiet) as pbar:
        async def search(semaphore, m):
            async with semaphore:
                result = await youtube.search(m['artist'], m['title'], m['duration'])
                pbar.update(1)
                await db.set_music_youtube(m['path'], result)
        semaphore = asyncio.BoundedSemaphore(concurrency)
        requests = [asyncio.ensure_future(search(semaphore, m)) for m in musics]
        await asyncio.gather(*requests)


@timeit
async def crawl_spotify(db, mf=None, concurrency=1):
    if mf is None:
        mf = Filter(spotify=[''])
    musics = await db.musics(mf)
    with tqdm(desc='Spotify musics', total=len(musics), disable=config.quiet) as pbar:
        async def search(semaphore, m):
            async with semaphore:
                result = await spotify.search(m['artist'], m['title'])
                pbar.update(1)
                await db.set_music_spotify(m['path'], result)
        semaphore = asyncio.BoundedSemaphore(concurrency)
        requests = [asyncio.ensure_future(search(semaphore, m)) for m in musics]
        await asyncio.gather(*requests)


@timeit
async def crawl_albums(db, mf=None, youtube_album='', concurrency=1):
    if mf is None:
        mf = Filter()
    albums = await db.albums(mf, youtube_album)
    with tqdm(desc='Youtube albums', total=len(albums), disable=config.quiet) as pbar:
        async def search(semaphore, a):
            async with semaphore:
                result = await youtube.search(a['artist'], a['name'] + ' full album', a['duration'])
                await db.set_album_youtube(a['name'], result)
                pbar.update(1)
        semaphore = asyncio.BoundedSemaphore(concurrency)
        requests = [asyncio.ensure_future(search(semaphore, a)) for a in albums]
        await asyncio.gather(*requests)


# from pydub import AudioSegment
# from pydub.utils import mediainfo
# seg = AudioSegment.from_file('original.mp3')
# seg.export('out.mp3', format='mp3', tags=mediainfo('original.mp3').get('TAG', {}))


pylint: disable-msg=too-many-locals
@cli.command()
@helpers.coro
@helpers.add_options(mfilter.options)
@click.argument('destination')
@click.pass_context
async def sync(ctx, destination, **kwargs):
    '''Copy selected musics with filters to destination folder'''
    import os
    from musicbot.lib import mfilter
    logger.info('Destination: %s', destination)
    ctx.obj.mf = mfilter.Filter(**kwargs)
    musics = ctx.obj.db.musics(ctx.obj.mf)

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




