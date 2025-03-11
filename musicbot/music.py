import logging
from dataclasses import asdict, dataclass
from pathlib import Path

from beartype import beartype
from beartype.typing import Any, Self
from slugify import slugify

from musicbot.defaults import REPLACEMENTS, STOPWORDS
from musicbot.folder import Folder
from musicbot.helpers import bytes_to_human, precise_seconds_to_human, yaml_dump
from musicbot.object import MusicbotObject
from musicbot.playlist_options import PlaylistOptions

logger = logging.getLogger(__name__)


@beartype
@dataclass(frozen=True)
class Music(MusicbotObject):
    title: str
    album: str
    artist: str
    genre: str
    size: int
    rating: float
    length: int
    keywords: frozenset[str]
    folders: frozenset[Folder]
    track: int | None = None
    # youtube: str | None = None
    # spotify: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(
            title=data["name"],
            album=data["album"]["name"],
            artist=data["artist"]["name"],
            genre=data["genre"]["name"],
            size=data["size"],
            rating=float(data["rating"]),
            length=data["length"],
            keywords=frozenset(keyword["name"] for keyword in data["keywords"]),
            folders=frozenset(Folder(name=folder["name"], ipv4=folder["ipv4"], username=folder["username"], path=Path(folder["path"])) for folder in data["folders"]),
            track=data["track"],
        )

    def human_repr(self) -> str:
        data: dict[str, Any] = asdict(self)
        data["size"] = bytes_to_human(data["size"])
        data["length"] = precise_seconds_to_human(data["length"])
        data["folders"] = list(folder.to_dict() for folder in data["folders"])
        data["keywords"] = list(data["keywords"])
        return yaml_dump(data)

    def links(self, playlist_options: PlaylistOptions | None = None) -> frozenset[str]:
        playlist_options = playlist_options if playlist_options is not None else PlaylistOptions()
        folder_links: list[str] = []
        for folder in self.folders:
            folder_links.extend(folder.links(playlist_options))
        return frozenset(folder_links)

    @property
    def slug(self) -> str:
        """Slugify music"""
        return slugify(
            f"""{self.artist}-{self.title}""",
            stopwords=STOPWORDS,
            replacements=REPLACEMENTS,
        )


@beartype
@dataclass
class MusicInput(MusicbotObject):
    title: str
    album: str
    artist: str
    genre: str
    size: int
    rating: float
    length: int
    keywords: list[str]
    ipv4: str
    username: str
    folder: str
    path: str
    track: int | None = None
