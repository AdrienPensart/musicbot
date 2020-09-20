import sys
from typing import Iterable, Dict, Optional, IO
from colorama import Fore  # type: ignore
from prettytable import PrettyTable  # type: ignore


def print_playlist(
    tracks: Iterable[Dict[str, str]],
    file: Optional[IO[str]] = None,
    current_title: Optional[str] = None,
    current_album: Optional[str] = None,
    current_artist: Optional[str] = None,
) -> None:
    if not tracks:
        return
    file = file if file is not None else sys.stdout
    pt = PrettyTable(["Title", "Album", "Artist"])
    for t in tracks:
        title = t.get('title', None)
        album = t.get('album', None)
        artist = t.get('artist', None)

        colored_title = (Fore.GREEN + title + Fore.RESET) if title == current_title else title
        colored_album = (Fore.GREEN + album + Fore.RESET) if album == current_album else album
        colored_artist = (Fore.GREEN + artist + Fore.RESET) if artist == current_artist else artist
        pt.add_row([colored_title, colored_album, colored_artist])
    print(pt, file=file)
