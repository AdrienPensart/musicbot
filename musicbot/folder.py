from dataclasses import asdict, dataclass
from pathlib import Path

import edgedb
from beartype import beartype
from beartype.typing import Self

from musicbot.object import MusicbotObject
from musicbot.playlist_options import PlaylistOptions


@beartype
@dataclass(frozen=True)
class Folder(MusicbotObject):
    name: str
    ipv4: str
    username: str
    path: Path

    n_genres: int = 0
    all_genres: str = ""

    n_artists: int = 0
    all_artists: str = ""

    n_keywords: int = 0
    all_keywords: str = ""

    n_albums: int = 0
    n_musics: int = 0
    human_size: str = ""
    human_duration: str = ""

    @classmethod
    def from_edgedb(
        cls,
        folder: edgedb.Object,
    ) -> Self:
        return cls(
            path=Path(folder.name),
            name=folder.name,
            ipv4=folder.ipv4,
            username=folder.username,
            n_artists=folder.n_artists,
            all_artists=folder.all_artists,
            n_albums=folder.n_albums,
            n_musics=folder.n_musics,
            n_keywords=folder.n_keywords,
            all_keywords=folder.all_keywords,
            n_genres=folder.n_genres,
            all_genres=folder.all_genres,
            human_size=folder.human_size,
            human_duration=folder.human_duration,
        )

    def __repr__(self) -> str:
        return f"{self.name} {self.ipv4} {self.username}"

    def to_dict(self) -> dict:
        data = asdict(self)
        data["path"] = str(data["path"])
        return data

    def effective_path(self, relative: bool = False) -> str:
        path = str(self.path)
        if relative:
            path = str(self.path.relative_to(self.name))
        return path.replace(" ", "\\ ")

    def http_link(self, relative: bool = False) -> str:
        return f"http://{self.ipv4}/{self.effective_path(relative)}"

    def local_ssh_link(self) -> str:
        return f"{self.username}@localhost:{self.path}"

    def remote_ssh_link(self) -> str:
        return f"{self.username}@{self.ipv4}:{self.path}"

    def links(self, playlist_options: PlaylistOptions) -> frozenset[str]:
        paths = []

        # if "local-ssh" in playlist_options.kinds and self.ipv4 == self.public_ip():
        if "all" in playlist_options.kinds or "local-ssh" in playlist_options.kinds:
            paths.append(self.local_ssh_link())

        # if "remote-ssh" in playlist_options.kinds and self.ipv4 != self.public_ip():
        if "all" in playlist_options.kinds or "remote-ssh" in playlist_options.kinds:
            paths.append(self.remote_ssh_link())

        # if "local-http" in playlist_options.kinds and self.ipv4 == self.public_ip():
        if "all" in playlist_options.kinds or "local-http" in playlist_options.kinds:
            paths.append(self.http_link(playlist_options.relative))

        # if "remote-http" in playlist_options.kinds and self.ipv4 != self.public_ip():
        if "all" in playlist_options.kinds or "remote-http" in playlist_options.kinds:
            paths.append(self.http_link(playlist_options.relative))

        if "all" in playlist_options.kinds or "local" in playlist_options.kinds and self.path.is_file():
            paths.append(self.effective_path(playlist_options.relative))

        if "all" in playlist_options.kinds or "remote" in playlist_options.kinds and not self.path.is_file():
            paths.append(self.effective_path(playlist_options.relative))

        return frozenset(paths)
