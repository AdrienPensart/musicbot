#!/usr/bin/env python

import unittest
import os
from asynctest import TestCase
from lib import file, database, lib, filter
from logging import DEBUG, getLogger

getLogger().setLevel(DEBUG)

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
        self.assertEqual(m.keywords, ["rock", "cutoff"])
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
        self.assertEqual(m.keywords, ["rap", "french"])
        self.assertEqual(m.rating, 4.5)
        self.assertEqual(m.duration, 258)

    def test_duration(self):
        self.assertEqual(12, lib.duration_to_seconds("12s"))
        self.assertEqual(60 * 12, lib.duration_to_seconds("12m"))
        self.assertEqual(60 * 60 * 12, lib.duration_to_seconds("12h"))

    def test_raise_limits(self):
        self.assertTrue(lib.raise_limits())


class DatabaseTest(TestCase):

    async def setUp(self):
        lib.verbose = False
        self.collection = database.DbContext(database='musicbot_test')
        self.files = list(lib.find_files(["tests/folder1", "tests/folder2"]))
        for f in self.files:
            m = file.File(f[1], f[0])
            await self.collection.upsert(m)

    async def tearDown(self):
        await self.collection.close()

    async def test_tag_filter(self):
        musics = await self.collection.filter(filter.Filter(genres=['Avantgarde']))
        self.assertEqual(len(musics), 4)
        musics = await self.collection.filter(filter.Filter(artists=['Buckethead']))
        self.assertEqual(len(musics), 4)
        musics = await self.collection.filter(filter.Filter(artists=['Buckethead'], min_rating=5.0))
        self.assertEqual(len(musics), 3)
        musics = await self.collection.filter(filter.Filter(artists=['Buckethead'], min_duration=2))
        self.assertEqual(len(musics), 0)
        musics = await self.collection.filter(filter.Filter(artists=['Buckethead'], keywords=['experimental']))
        self.assertEqual(len(musics), 2)
        musics = await self.collection.filter(filter.Filter(artists=['Buckethead'], no_keywords=['heavy']))
        self.assertEqual(len(musics), 3)
        musics = await self.collection.filter(filter.Filter(artists=['1995']))
        self.assertEqual(len(musics), 1)

    async def test_new_playlist(self):
        mf = filter.Filter(relative=True)
        playlist = await self.collection.playlist(mf)
        final = """#EXTM3U
Buckethead/1994 - Giant Robot/02 - Welcome To Bucketheadland.flac
Buckethead/1994 - Giant Robot/02 - Welcome To Bucketheadland - Cut.flac
Buckethead/1994 - Giant Robot/03 - I Come In Peace.flac
1995/La Source/La Flemme.mp3
Buckethead/1994 - Giant Robot/01 - Doomride.flac"""
        self.maxDiff = None
        self.assertMultiLineEqual(playlist['content'], final)
        print('Output:', playlist['content'])
        print('Final:', final)

    async def test_stats(self):
        stats = await self.collection.stats()
        self.assertEqual(dict(stats), teststats)

    async def test_filtered_stats(self):
        mf = filter.Filter(keywords=['rock'])
        stats = await self.collection.stats(mf)
        self.assertEqual(dict(stats), filtered_teststats)


if __name__ == '__main__':
    unittest.main()
