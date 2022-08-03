from pathlib import Path

my_dir = Path(__file__).resolve().parent

first_name = "first_test"
last_name = "last_test"
email = "test@test.com"
password = "test_test"

folder_flac = my_dir / "fixtures" / "folder1"
folder_mp3 = my_dir / "fixtures" / "folder2"
folders = [str(folder_flac), str(folder_mp3)]
youtube_url = "https://www.youtube.com/watch?v=rIlLqmI_VkE"

one_flac = folder_flac / "Buckethead" / "1994 - Giant Robot" / "02 - Welcome To Bucketheadland.flac"
one_mp3 = folder_mp3 / "1995" / "La Source" / "La Flemme.mp3"

teststats = {
    'id': 1,
    'musics': 5,
    'links': 10,
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
    'links': 4,
    'genres': 1,
    'albums': 1,
    'duration': 2,
    'artists': 1,
    'keywords': 3,
    'size': 120219
}
