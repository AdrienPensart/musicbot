import logging
from .helpers import timeit
from .file import File, supported_formats
from .lib import find_files

logger = logging.getLogger(__name__)


@timeit
def genmusics(folders):
    return [File(f[1], f[0]).to_dict() for f in find_files(list(folders)) if f[1].endswith(tuple(supported_formats))]


# from .config import config
# from .mfilter import Filter, supported_formats
# from . import youtube, spotify
# @timeit
# async def crawl_musics(db, mf=None, concurrency=1):
#     if mf is None:
#         mf = Filter(youtubes=[''])
#     musics = await db.musics(mf)
#     with tqdm(desc='Youtube musics', total=len(musics), disable=config.quiet) as pbar:
#         async def search(semaphore, m):
#             async with semaphore:
#                 result = await youtube.search(m['artist'], m['title'], m['duration'])
#                 pbar.update(1)
#                 await db.set_music_youtube(m['path'], result)
#         semaphore = asyncio.BoundedSemaphore(concurrency)
#         requests = [asyncio.ensure_future(search(semaphore, m)) for m in musics]
#         await asyncio.gather(*requests)
#
#
# @timeit
# async def crawl_spotify(db, mf=None, concurrency=1):
#     if mf is None:
#         mf = Filter(spotify=[''])
#     musics = await db.musics(mf)
#     with tqdm(desc='Spotify musics', total=len(musics), disable=config.quiet) as pbar:
#         async def search(semaphore, m):
#             async with semaphore:
#                 result = await spotify.search(m['artist'], m['title'])
#                 pbar.update(1)
#                 await db.set_music_spotify(m['path'], result)
#         semaphore = asyncio.BoundedSemaphore(concurrency)
#         requests = [asyncio.ensure_future(search(semaphore, m)) for m in musics]
#         await asyncio.gather(*requests)


# @timeit
# async def crawl_albums(db, mf=None, youtube_album='', concurrency=1):
#     if mf is None:
#         mf = Filter()
#     albums = await db.albums(mf, youtube_album)
#     with tqdm(desc='Youtube albums', total=len(albums), disable=config.quiet) as pbar:
#         async def search(semaphore, a):
#             async with semaphore:
#                 result = await youtube.search(a['artist'], a['name'] + ' full album', a['duration'])
#                 await db.set_album_youtube(a['name'], result)
#                 pbar.update(1)
#         semaphore = asyncio.BoundedSemaphore(concurrency)
#         requests = [asyncio.ensure_future(search(semaphore, a)) for a in albums]
#         await asyncio.gather(*requests)
