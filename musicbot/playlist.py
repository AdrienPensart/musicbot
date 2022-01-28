from typing import Iterable, Dict, Optional
from rich.table import Table
import click
from musicbot.object import MusicbotObject


def print_playlist(
    tracks: Iterable[Dict[str, str]],
    current_title: Optional[str] = None,
    current_album: Optional[str] = None,
    current_artist: Optional[str] = None,
) -> None:
    if not tracks:
        return
    table = Table("Title", "Album", "Artist")
    for t in tracks:
        title = t.get('title', None)
        album = t.get('album', None)
        artist = t.get('artist', None)

        colored_title = click.style(title, fg="green") if title == current_title else title
        colored_album = click.style(album, fg="green") if album == current_album else album
        colored_artist = click.style(artist, fg="green") if artist == current_artist else artist
        table.add_row(colored_title, colored_album, colored_artist)
    MusicbotObject.console.print(table)
