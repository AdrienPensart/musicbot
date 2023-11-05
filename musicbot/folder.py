import os
from dataclasses import dataclass

from beartype import beartype

from musicbot.object import MusicbotObject
from musicbot.playlist_options import PlaylistOptions


@beartype
@dataclass(frozen=True)
class Folder(MusicbotObject):
    name: str
    ipv4: str
    user: str
    path: str

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

    def __repr__(self) -> str:
        return f"{self.name} {self.ipv4} {self.user}"

    def effective_path(self, relative: bool = False) -> str:
        if relative:
            return self.path[len(self.name) + 1 :]
        return self.path

    def http_link(self, relative: bool = False) -> str:
        return f"http://{self.ipv4}/{self.effective_path(relative)}"

    def ssh_link(self) -> str:
        return f"{self.user}@{self.ipv4}:{self.path}"

    def links(self, playlist_options: PlaylistOptions) -> frozenset[str]:
        paths = []
        if "all" in playlist_options.kinds:
            return frozenset({self.ssh_link(), self.http_link(playlist_options.relative), self.effective_path(playlist_options.relative)})

        if "local-ssh" in playlist_options.kinds and self.ipv4 == self.public_ip():
            paths.append(self.ssh_link())
        if "remote-ssh" in playlist_options.kinds and self.ipv4 != self.public_ip():
            paths.append(self.ssh_link())

        if "local-http" in playlist_options.kinds and self.ipv4 == self.public_ip():
            paths.append(self.http_link(playlist_options.relative))
        if "remote-http" in playlist_options.kinds and self.ipv4 != self.public_ip():
            paths.append(self.http_link(playlist_options.relative))

        if "local" in playlist_options.kinds and os.path.isfile(self.path):
            paths.append(self.effective_path(playlist_options.relative))
        if "remote" in playlist_options.kinds and not os.path.isfile(self.path):
            paths.append(self.effective_path(playlist_options.relative))
        return frozenset(paths)
