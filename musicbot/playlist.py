import sys
from prettytable import PrettyTable
from musicbot.helpers import Green, Reset


def print_playlist(tracks, file=None, current_title=None, current_album=None, current_artist=None):
    file = file if file is not None else sys.stdout
    pt = PrettyTable()
    pt.field_names = [
        "Title",
        "Album",
        "Artist",
    ]
    for t in tracks:
        title = (Green + t['title'] + Reset) if t['title'] == current_title else t['title']
        album = (Green + t['album'] + Reset) if t['album'] == current_album else t['album']
        artist = (Green + t['artist'] + Reset) if t['artist'] == current_artist else t['artist']
        pt.add_row([title, album, artist])
    print(pt, file=file)
