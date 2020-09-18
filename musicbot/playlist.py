import sys
from colorama import Fore  # type: ignore
from prettytable import PrettyTable  # type: ignore


def print_playlist(tracks, file=None, current_title=None, current_album=None, current_artist=None):
    if not tracks:
        return
    file = file if file is not None else sys.stdout
    pt = PrettyTable(["Title", "Album", "Artist"])
    for t in tracks:
        title = (Fore.GREEN + t['title'] + Fore.RESET) if t['title'] == current_title else t['title']
        album = (Fore.GREEN + t['album'] + Fore.RESET) if t['album'] == current_album else t['album']
        artist = (Fore.GREEN + t['artist'] + Fore.RESET) if t['artist'] == current_artist else t['artist']
        pt.add_row([title, album, artist])
    print(pt, file=file)
