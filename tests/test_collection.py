import os
import logging
import pytest
from musicbot.lib.database import MB_DB, DEFAULT_DB, Database
from musicbot.lib import lib, file
from . import fixtures

logger = logging.getLogger(__name__)


@pytest.fixture
def files():
    return list(lib.find_files(fixtures.folders))


@pytest.yield_fixture
async def db(files, worker_id):
    # if running pytest with xdist
    # append worker ID to test database name
    db_name = os.getenv(MB_DB, DEFAULT_DB)
    db_name += ("_" + worker_id)
    db = await Database.make(db=db_name)
    await db.clear()
    await db.register_user(email="test@test.com", password="test", first_name="test", last_name="test")
    await db.authenticate_user(email="test@test.com", password="test")
    for f in files:
        m = file.File(f[1], f[0])
        await db.upsert(m)
    yield db
    await db.drop()


async def test_filters(db):
    await db.execute('select * from musicbot_public.default_filters()')
    filters = await db.filters()
    assert len(filters) == 9

# async def test_folders(db):
#     folders = await db.folders_name()
#     assert folders == fixtures.folders
#
#
# async def test_artists(db):
#     artists = await db.artists_name()
#     assert artists == ['1995', 'Buckethead']
#
#
# async def test_keywords(db):
#     keywords = await db.keywords_name()
#     assert keywords == ['cut', 'cutoff', 'experimental', 'french', 'heavy', 'intro', 'rap', 'rock', 'talkover']
#
#
# async def test_albums(db):
#     albums = await db.albums_name()
#     assert albums == ['Giant Robot', 'La Source']
#
#
# async def test_genres(db):
#     genres = await db.genres_name()
#     assert genres == ['Avantgarde', 'Rap']
#
#
# async def test_titles(db):
#     titles = await db.titles_name()
#     assert titles == ['Doomride', 'I Come In Peace', 'La Flemme', 'Welcome To Bucketheadland', 'Welcome To Bucketheadland - Cut']
#
#
# async def test_tag_filter(db):
#     musics = await db.musics(mfilter.Filter(genres=['Avantgarde']))
#     assert len(musics) == 4
#     musics = await db.musics(mfilter.Filter(artists=['Buckethead']))
#     assert len(musics) == 4
#     musics = await db.musics(mfilter.Filter(artists=['Buckethead'], min_rating=5.0))
#     assert len(musics) == 3
#     musics = await db.musics(mfilter.Filter(artists=['Buckethead'], min_duration=2))
#     assert len(musics) == 0
#     musics = await db.musics(mfilter.Filter(artists=['Buckethead'], keywords=['experimental']))
#     assert len(musics) == 2
#     musics = await db.musics(mfilter.Filter(artists=['Buckethead'], no_keywords=['heavy']))
#     assert len(musics) == 3
#     musics = await db.musics(mfilter.Filter(artists=['1995']))
#     assert len(musics) == 1
#     musics = await db.musics(mfilter.Filter(youtubes=['']))
#     assert len(musics) == 5
#
#
# async def test_new_playlist(db):
#     mf = mfilter.Filter(relative=True)
#     playlist = await db.playlist(mf)
#     final = """#EXTM3U
# 1995/La Source/La Flemme.mp3
# Buckethead/1994 - Giant Robot/01 - Doomride.flac
# Buckethead/1994 - Giant Robot/02 - Welcome To Bucketheadland.flac
# Buckethead/1994 - Giant Robot/02 - Welcome To Bucketheadland - Cut.flac
# Buckethead/1994 - Giant Robot/03 - I Come In Peace.flac"""
#     assert playlist['content'] == final
#     print('Output:', playlist['content'])
#     print('Final:', final)
#
#
# async def test_stats(db):
#     stats = await db.stats()
#     assert dict(stats) == fixtures.teststats
#
#
# async def test_filtered_stats(db):
#     mf = mfilter.Filter(keywords=['rock'])
#     stats = await db.stats(mf)
#     assert dict(stats) == fixtures.filtered_teststats
