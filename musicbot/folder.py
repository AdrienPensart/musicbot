from dataclasses import asdict, dataclass
from pathlib import Path

from beartype import beartype

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
