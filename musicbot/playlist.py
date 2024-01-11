import itertools
import logging
import random
from codecs import StreamReaderWriter
from dataclasses import asdict, dataclass
from pathlib import Path

import click
import edgedb
from beartype import beartype
from beartype.typing import Self
from click_skeleton.helpers import PrettyDefaultDict
from click_skeleton.helpers import seconds_to_human as formatted_seconds_to_human
from more_itertools import interleave_evenly
from rich.table import Column, Table
from rich.text import Text

from musicbot.file import File
from musicbot.folder import Folder
from musicbot.helpers import bytes_to_human, precise_seconds_to_human
from musicbot.music import Music
from musicbot.object import MusicbotObject
from musicbot.playlist_options import PlaylistOptions

logging.getLogger("vlc").setLevel(logging.NOTSET)
logger = logging.getLogger(__name__)


@beartype
@dataclass(frozen=True)
class Playlist(MusicbotObject):
    name: str
    musics: list[Music]

    @classmethod
    def from_files(
        cls,
        name: str,
        files: list[File],
    ) -> Self:
        musics = [file.music for file in files if file.music is not None]
        return cls(name=name, musics=musics)

    @classmethod
    def from_edgedb(
        cls,
        name: str,
        results: list[edgedb.Object],
    ) -> Self:
        musics = []
        for result in results:
            keywords = frozenset(keyword.name for keyword in result.keywords)
            # folders = frozenset(Folder(path=Path(folder["@path"]), name=folder.name, ipv4=folder.ipv4, username=folder.username) for folder in result.folders)
            folders = frozenset(Folder(path=Path(folder.path), name=folder.name, ipv4=folder.ipv4, username=folder.username) for folder in result.folders)
            music = Music(
                title=result.name,
                artist=result.artist.name,
                album=result.album.name,
                genre=result.genre.name,
                size=result.size,
                length=result.length,
                keywords=keywords,
                track=result.track,
                rating=result.rating,
                folders=folders,
            )
            musics.append(music)

        return cls(
            name=name,
            musics=musics,
        )

    def print(
        self,
        output: str,
        current_title: str | None = None,
        current_album: str | None = None,
        current_artist: str | None = None,
        file: click.utils.LazyFile | StreamReaderWriter | None = None,
        playlist_options: PlaylistOptions | None = None,
    ) -> None:
        playlist_options = playlist_options if playlist_options is not None else PlaylistOptions()
        musics = self.musics
        if playlist_options.interleave:
            musics_by_artist = PrettyDefaultDict(list)
            for music in self.musics:
                musics_by_artist[music.artist].append(music)
            musics = list(interleave_evenly([list(value) for value in musics_by_artist.values()]))

        if playlist_options.shuffle:
            random.shuffle(musics)

        table = Table(
            Column("Music", vertical="middle"),
            Column("Infos", vertical="middle"),
            Column("Links", no_wrap=True),
            show_lines=True,
            title=f"Playlist: {self.name}",
        )
        total_length = 0
        total_size = 0
        for music in musics:
            raw_row: list[str] = [
                "\n".join([f"{music.track} - {music.title}", music.artist, music.album, music.genre]),
                "\n".join([str(music.rating), ",".join(sorted(music.keywords)), formatted_seconds_to_human(music.length), bytes_to_human(music.size)]),
                "\n".join(sorted(music.links(playlist_options))),
            ]
            if music.title == current_title and music.album == current_album and music.artist == current_artist:
                colored_row = [Text(elem, style="green") for elem in raw_row]
                table.add_row(*colored_row)
            else:
                table.add_row(*raw_row)

            total_length += music.length
            total_size += music.size

        caption = f"Songs: {len(musics)} | Total length: {precise_seconds_to_human(total_length)} | Total size: {bytes_to_human(total_size)}"
        table.caption = caption

        if not musics and output != "json":
            pass
        elif output == "m3u":
            p = "#EXTM3U\n"
            p += "#EXTREM:" + self.name + "\n"
            p += "\n".join(self.links(playlist_options))
            print(p, file=file)
            self.success(caption)
        elif output == "table":
            self.print_table(table, file=file)
        elif output == "json":
            # self.print_json(asdict(self, recurse=True), file=file)
            self.print_json(asdict(self), file=file)
            self.success(caption)
        else:
            self.err(f"unknown output type : {output}")

    def __repr__(self) -> str:
        # self_dict = asdict(self, recurse=True)
        self_dict = asdict(self)
        if (representation := self.dumps_json(self_dict)) is not None:
            return representation
        self.err(f"Unable to convert to json : {self_dict}")
        return "{}"

    @property
    def genres(self) -> frozenset[str]:
        return frozenset(set(music.genre for music in self.musics))

    @property
    def albums(self) -> frozenset[str]:
        return frozenset(set(music.album for music in self.musics))

    @property
    def artists(self) -> frozenset[str]:
        return frozenset(set(music.artist for music in self.musics))

    @property
    def keywords(self) -> frozenset[str]:
        return frozenset(itertools.chain(*[music.keywords for music in self.musics]))

    @property
    def ratings(self) -> frozenset[float]:
        return frozenset(set(music.rating for music in self.musics))

    def links(self, playlist_options: PlaylistOptions) -> list[str]:
        return list(itertools.chain(*[music.links(playlist_options) for music in self.musics]))
