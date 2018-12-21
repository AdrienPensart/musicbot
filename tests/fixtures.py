import os

my_dir = os.path.dirname(os.path.abspath(__file__))

email = "test@test.com"
password = "test_test"

folder1 = my_dir + "/fixtures/folder1"
folder2 = my_dir + "/fixtures/folder2"
folders = [folder1, folder2]

one_flac = folder1 + "/Buckethead/1994 - Giant Robot/02 - Welcome To Bucketheadland.flac"
one_mp3 = folder2 + "/1995/La Source/La Flemme.mp3"

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
