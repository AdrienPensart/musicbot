import pytest
import logging
from lib.collection import Collection
from lib import lib, file, mfilter
from . import fixtures

logger = logging.getLogger(__name__)


@pytest.fixture
def files():
    return list(lib.find_files(fixtures.folders))


@pytest.yield_fixture
async def collection(files):
    logger.debug('new collection')
    collection = await Collection.make()
    await collection.clear()
    for f in files:
        m = file.File(f[1], f[0])
        await collection.upsert(m)
    await collection.refresh()
    yield collection
    await collection.close()


async def test_folders(collection):
    folders = await collection.folders_name()
    assert folders == fixtures.folders


async def test_artists(collection):
    artists = await collection.artists_name()
    assert artists == ['1995', 'Buckethead']


async def test_keywords(collection):
    keywords = await collection.keywords_name()
    assert keywords == ['cut', 'cutoff', 'experimental', 'french', 'heavy', 'intro', 'rap', 'rock', 'talkover']


async def test_albums(collection):
    albums = await collection.albums_name()
    assert albums == ['Giant Robot', 'La Source']


async def test_genres(collection):
    genres = await collection.genres_name()
    assert genres == ['Avantgarde', 'Rap']


async def test_titles(collection):
    titles = await collection.titles_name()
    assert titles == ['Doomride', 'I Come In Peace', 'La Flemme', 'Welcome To Bucketheadland', 'Welcome To Bucketheadland - Cut']


async def test_tag_filter(collection):
    musics = await collection.musics(mfilter.Filter(genres=['Avantgarde']))
    assert len(musics) == 4
    musics = await collection.musics(mfilter.Filter(artists=['Buckethead']))
    assert len(musics) == 4
    musics = await collection.musics(mfilter.Filter(artists=['Buckethead'], min_rating=5.0))
    assert len(musics) == 3
    musics = await collection.musics(mfilter.Filter(artists=['Buckethead'], min_duration=2))
    assert len(musics) == 0
    musics = await collection.musics(mfilter.Filter(artists=['Buckethead'], keywords=['experimental']))
    assert len(musics) == 2
    musics = await collection.musics(mfilter.Filter(artists=['Buckethead'], no_keywords=['heavy']))
    assert len(musics) == 3
    musics = await collection.musics(mfilter.Filter(artists=['1995']))
    assert len(musics) == 1
    musics = await collection.musics(mfilter.Filter(youtubes=['']))
    assert len(musics) == 5


async def test_new_playlist(collection):
    mf = mfilter.Filter(relative=True)
    playlist = await collection.playlist(mf)
    final = """#EXTM3U
1995/La Source/La Flemme.mp3
Buckethead/1994 - Giant Robot/01 - Doomride.flac
Buckethead/1994 - Giant Robot/02 - Welcome To Bucketheadland.flac
Buckethead/1994 - Giant Robot/02 - Welcome To Bucketheadland - Cut.flac
Buckethead/1994 - Giant Robot/03 - I Come In Peace.flac"""
    assert playlist['content'] == final
    print('Output:', playlist['content'])
    print('Final:', final)


async def test_stats(collection):
    stats = await collection.stats()
    assert dict(stats) == fixtures.teststats


async def test_filtered_stats(collection):
    mf = mfilter.Filter(keywords=['rock'])
    stats = await collection.stats(mf)
    assert dict(stats) == fixtures.filtered_teststats
