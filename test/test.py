#!/usr/bin/env python3
import unittest
import os
import asynctest
import logging

from lib import file, collection, lib, mfilter
from lib.config import config
from lib.server import app
from lib.web.config import webconfig

webconfig.no_auth = True
config.set()
logger = logging.getLogger(__name__)

my_dir = os.path.dirname(os.path.abspath(__file__))

folder1 = my_dir + "/fixtures/folder1"
folder2 = my_dir + "/fixtures/folder2"
flac = "/Buckethead/1994 - Giant Robot/02 - Welcome To Bucketheadland.flac"
teststats = {
    'id': 1,
    'musics': 5,
    'genres': 2,
    'albums': 2,
    'duration': 262,
    'artists': 2,
    'keywords': 9,
    'size': 7305444
}
filtered_teststats = {
    'id': 1,
    'musics': 2,
    'genres': 1,
    'albums': 1,
    'duration': 2,
    'artists': 1,
    'keywords': 3,
    'size': 120219
}


class ApiTest(unittest.TestCase):
    def test_index(self):
        _, response = app.test_client.get('/')
        self.assertEqual(response.status, 200)

    def test_collection_filters(self):
        _, response = app.test_client.get('/collection/filters')
        self.assertEqual(response.status, 200)


class MusicTagsTest(unittest.TestCase):

    def test_finding_files(self):
        files = list(lib.find_files([folder1, folder2]))
        self.assertEqual(len(files), 5)

    def test_flac_tags(self):
        m = file.File(folder1 + flac, folder1)

        self.assertEqual(m.artist, "Buckethead")
        self.assertEqual(m.title, "Welcome To Bucketheadland")
        self.assertEqual(m.album, "Giant Robot")
        self.assertEqual(m.genre, "Avantgarde")
        self.assertEqual(m.number, 2)
        self.assertEqual(m.description, "rock cutoff")
        self.assertEqual(m.keywords, "rock cutoff")
        self.assertEqual(m.rating, 5.0)
        self.assertEqual(m.duration, 1)

    def test_mp3_tags(self):
        m = file.File(folder2 + "/1995/La Source/La Flemme.mp3", folder2)

        self.assertEqual(m.artist, "1995")
        self.assertEqual(m.title, "La Flemme")
        self.assertEqual(m.album, "La Source")
        self.assertEqual(m.genre, "Rap")
        self.assertEqual(m.number, 2)
        self.assertEqual(m.comment, "rap french")
        self.assertEqual(m.keywords, "rap french")
        self.assertEqual(m.rating, 4.5)
        self.assertEqual(m.duration, 258)

    def test_duration(self):
        self.assertEqual(12, lib.duration_to_seconds("12s"))
        self.assertEqual(60 * 12, lib.duration_to_seconds("12m"))
        self.assertEqual(60 * 60 * 12, lib.duration_to_seconds("12h"))

    def test_raise_limits(self):
        self.assertTrue(lib.raise_limits())


class DatabaseTest(asynctest.TestCase):

    async def setUp(self):
        self.collection = collection.Collection(db_database='musicbot_test')
        await self.collection.clear(os.path.join(my_dir, '../schema'))
        self.files = list(lib.find_files([folder1, folder2]))
        for f in self.files:
            m = file.File(f[1], f[0])
            await self.collection.upsert(m)
        await self.collection.refresh()

    async def tearDown(self):
        await self.collection.close()

    async def test_folders(self):
        folders = await self.collection.folders_name()
        self.assertEqual(folders, [folder1, folder2])

    async def test_artists(self):
        artists = await self.collection.artists_name()
        self.assertEqual(artists, ['1995', 'Buckethead'])

    async def test_keywords(self):
        keywords = await self.collection.keywords_name()
        self.assertEqual(keywords, ['cut', 'cutoff', 'experimental', 'french', 'heavy', 'intro', 'rap', 'rock', 'talkover'])

    async def test_albums(self):
        albums = await self.collection.albums_name()
        self.assertEqual(albums, ['Giant Robot', 'La Source'])

    async def test_genres(self):
        genres = await self.collection.genres_name()
        self.assertEqual(genres, ['Avantgarde', 'Rap'])

    async def test_titles(self):
        titles = await self.collection.titles_name()
        self.assertEqual(titles, ['Doomride', 'I Come In Peace', 'La Flemme', 'Welcome To Bucketheadland', 'Welcome To Bucketheadland - Cut'])

    async def test_tag_filter(self):
        musics = await self.collection.musics(mfilter.Filter(genres=['Avantgarde']))
        self.assertEqual(len(musics), 4)
        musics = await self.collection.musics(mfilter.Filter(artists=['Buckethead']))
        self.assertEqual(len(musics), 4)
        musics = await self.collection.musics(mfilter.Filter(artists=['Buckethead'], min_rating=5.0))
        self.assertEqual(len(musics), 3)
        musics = await self.collection.musics(mfilter.Filter(artists=['Buckethead'], min_duration=2))
        self.assertEqual(len(musics), 0)
        musics = await self.collection.musics(mfilter.Filter(artists=['Buckethead'], keywords=['experimental']))
        self.assertEqual(len(musics), 2)
        musics = await self.collection.musics(mfilter.Filter(artists=['Buckethead'], no_keywords=['heavy']))
        self.assertEqual(len(musics), 3)
        musics = await self.collection.musics(mfilter.Filter(artists=['1995']))
        self.assertEqual(len(musics), 1)
        musics = await self.collection.musics(mfilter.Filter(youtubes=['']))
        self.assertEqual(len(musics), 5)

    async def test_new_playlist(self):
        mf = mfilter.Filter(relative=True)
        playlist = await self.collection.playlist(mf)
        final = """#EXTM3U
1995/La Source/La Flemme.mp3
Buckethead/1994 - Giant Robot/01 - Doomride.flac
Buckethead/1994 - Giant Robot/02 - Welcome To Bucketheadland - Cut.flac
Buckethead/1994 - Giant Robot/02 - Welcome To Bucketheadland.flac
Buckethead/1994 - Giant Robot/03 - I Come In Peace.flac"""
        self.maxDiff = None
        self.assertMultiLineEqual(playlist['content'], final)
        print('Output:', playlist['content'])
        print('Final:', final)

    async def test_stats(self):
        stats = await self.collection.stats()
        self.assertEqual(dict(stats), teststats)

    async def test_filtered_stats(self):
        mf = mfilter.Filter(keywords=['rock'])
        stats = await self.collection.stats(mf)
        self.assertEqual(dict(stats), filtered_teststats)


if __name__ == '__main__':
    unittest.main()
