import logging
import shutil
from dataclasses import asdict, dataclass
from enum import Enum, unique
from functools import cached_property
from pathlib import Path, PurePath

import acoustid  # type: ignore
from beartype import beartype
from beartype.typing import Any, Self
from click_skeleton.helpers import mysplit
from mutagen import File as MutagenFile
from mutagen import MutagenError, id3
from pydub import AudioSegment  # type: ignore
from shazamio import Shazam  # type: ignore

from musicbot.defaults import (
    DEFAULT_EXTENSIONS,
    DEFAULT_MAX_RATING,
    DEFAULT_MIN_RATING,
    RATING_CHOICES,
    STORED_RATING_CHOICES,
)
from musicbot.folder import Folder
from musicbot.helpers import current_user
from musicbot.music import Music, MusicInput
from musicbot.object import MusicbotObject

logger = logging.getLogger(__name__)


@unique
class Issue(str, Enum):
    NO_TITLE = "no-title"
    NO_GENRE = "no-genre"
    NO_ALBUM = "no-album"
    NO_ARTIST = "no-artist"
    NO_RATING = "no-rating"
    NO_TRACK = "no-track"
    INVALID_COMMENT = "invalid-comment"
    INVALID_TITLE = "invalid-title"
    INVALID_PATH = "invalid-path"


@beartype
@dataclass
class File(MusicbotObject):
    folder: Path
    handle: Any

    @classmethod
    def from_path(cls, folder: Path, path: Path) -> Self | None:
        if not str(path).endswith(tuple(DEFAULT_EXTENSIONS)):
            cls.err(f"{path} : not supported ({DEFAULT_EXTENSIONS})")
            return None

        try:
            return cls(folder=folder.resolve(), handle=MutagenFile(path.resolve()))
        except MutagenError as error:
            cls.err(f"Unable to instanciate {path}", error=error)
        return None

    def __repr__(self) -> str:
        return str(self.path)

    @property
    def issues(self) -> set[Issue]:
        issues = set()
        if not self.title:
            issues.add(Issue.NO_TITLE)
        if not self.genre:
            issues.add(Issue.NO_GENRE)
        if not self.album:
            issues.add(Issue.NO_ALBUM)
        if not self.artist:
            issues.add(Issue.NO_ARTIST)
        if self.rating == -1:
            issues.add(Issue.NO_RATING)
        if self.track == -1:
            issues.add(Issue.NO_TRACK)
        if self.extension == ".flac" and self._comment and not self._description:
            issues.add(Issue.INVALID_COMMENT)
        if self.extension == ".mp3" and self._description and not self._comment:
            issues.add(Issue.INVALID_COMMENT)
        if self.track not in (-1, 0) and self.title != self.canonic_title:
            logger.debug(f"{self} : invalid title, '{self.title}' should be '{self.canonic_title}'")
            issues.add(Issue.INVALID_TITLE)
        if self.track not in (-1, 0) and not str(self.path).endswith(str(self.canonic_artist_album_filename)):
            logger.debug(f"{self} : invalid path, must have a track and should end with '{self.canonic_artist_album_filename}'")
            issues.add(Issue.INVALID_PATH)
        return issues

    @property
    def music(self) -> Music | None:
        if (public_ip := self.public_ip()) is None:
            return None
        folder = Folder(
            name=str(self.folder),
            path=self.path,
            username=current_user(),
            ipv4=public_ip,
        )
        return Music(
            title=self.title,
            size=self.size,
            album=self.album,
            artist=self.artist,
            genre=self.genre,
            length=self.length,
            track=self.track,
            rating=self.rating,
            keywords=frozenset(self.keywords),
            folders=frozenset({folder}),
        )

    @property
    def music_input(self) -> MusicInput | None:
        if (music := self.music) is None:
            return None
        if not music.folders:
            self.err(f"{self} : no folder set")
            return None

        data = asdict(music)

        folders = data.pop("folders")
        folder = next(iter(folders))
        data["keywords"] = list(data["keywords"])
        data["ipv4"] = folder.ipv4
        data["username"] = folder.username
        data["folder"] = folder.name
        data["path"] = str(folder.path)
        return MusicInput(**data)

    def set_tags(
        self,
        title: str | None = None,
        artist: str | None = None,
        album: str | None = None,
        genre: str | None = None,
        keywords: list[str] | None = None,
        rating: float | None = None,
        track: int | None = None,
    ) -> bool:
        if title is not None:
            self.title = title
        if artist is not None:
            self.artist = artist
        if album is not None:
            self.album = album
        if genre is not None:
            self.genre = genre
        if keywords is not None:
            self.keywords = set(keywords)
        if rating is not None:
            self.rating = rating
        if track is not None:
            self.track = track
        return self.save()

    @cached_property
    def size(self) -> int:
        return self.path.stat().st_size

    @property
    def path(self) -> Path:
        return Path(self.handle.filename)

    @property
    def canonic_path(self) -> Path:
        return self.folder / self.canonic_artist_album_filename

    # @property
    # def youtube(self) -> str | None:
    #     return None

    # @property
    # def spotify(self) -> str | None:
    #     return None

    @property
    def extension(self) -> str:
        return self.path.suffix

    @property
    def canonic_artist_album_filename(self) -> PurePath:
        return PurePath(self.artist, self.album, self.canonic_filename)

    @property
    def filename(self) -> str:
        return self.path.name

    @property
    def canonic_title(self) -> str:
        prefix = f"{str(self.track).zfill(2)} - "
        if not self.title.startswith(prefix):
            return f"{prefix}{self.title}"
        return self.title

    @property
    def canonic_filename(self) -> str:
        return f"{self.canonic_title}{self.extension}"

    @property
    def flat_title(self) -> str:
        return f"{self.artist} - {self.album} - {self.canonic_title}"

    @property
    def flat_filename(self) -> str:
        return f"{self.artist} - {self.album} - {self.canonic_title}{self.extension}"

    @property
    def flat_path(self) -> Path:
        return self.folder / self.flat_filename

    def _get_first(self, tag: str, default: str = "") -> str:
        if tag not in self.handle:
            return default
        for item in self.handle[tag]:
            return str(item)
        return default

    @property
    def length(self) -> int:
        return int(self.handle.info.length)

    @property
    def title(self) -> str:
        if self.extension == ".flac":
            return self._get_first("title")
        return self._get_first("TIT2")

    @title.setter
    def title(self, title: str) -> None:
        if self.extension == ".flac":
            self.handle.tags["title"] = title
        else:
            self.handle.tags.add(id3.TIT2(text=title))

    @property
    def album(self) -> str:
        if self.extension == ".flac":
            return self._get_first("album")
        return self._get_first("TALB")

    @album.setter
    def album(self, album: str) -> None:
        if self.extension == ".flac":
            self.handle.tags["album"] = album
        else:
            self.handle.tags.add(id3.TALB(text=album))

    @property
    def artist(self) -> str:
        if self.extension == ".flac":
            return self._get_first("artist")
        return self._get_first("TPE1")

    @artist.setter
    def artist(self, artist: str) -> None:
        if self.extension == ".flac":
            self.handle.tags["artist"] = artist
        else:
            self.handle.tags.add(id3.TPE1(text=artist))

    @property
    def genre(self) -> str:
        if self.extension == ".flac":
            genre = self._get_first("genre")
        else:
            genre = self._get_first("TCON")
        if not genre:
            logger.debug(f"{self} : no genre set")
        return genre

    @genre.setter
    def genre(self, genre: str) -> None:
        if self.extension == ".flac":
            self.handle.tags["genre"] = genre
        else:
            self.handle.tags.add(id3.TCON(text=genre))

    @property
    def rating(self) -> float:
        if self.extension == ".flac":
            rating_str = self._get_first("fmps_rating")
        else:
            rating_str = self._get_first("TXXX:FMPS_Rating")
        try:
            rating = float(rating_str)
            if rating not in STORED_RATING_CHOICES:
                self.err(f"{self} : badly stored rating : '{rating}'", only_once=True)
                return 0.0

            rating *= 5.0
            if rating < DEFAULT_MIN_RATING:
                return DEFAULT_MIN_RATING
            if rating > DEFAULT_MAX_RATING:
                return DEFAULT_MAX_RATING
            return rating
        except ValueError:
            self.warn(f"{self} : cannot convert rating to float : '{rating_str}', try fixing")
            self.rating = 0.0
            if not self.save():
                self.err(f"{self} : unable to fix rating")
            return 0.0

    @rating.setter
    def rating(self, rating: float) -> None:
        if rating not in RATING_CHOICES:
            self.err(f"{self} : tried to set a bad rating : {rating}")
            return
        rating /= 5.0
        if self.extension == ".flac":
            self.handle["fmps_rating"] = str(rating)
        else:
            txxx = id3.TXXX(desc="FMPS_Rating", text=str(rating))
            self.handle.tags.add(txxx)

    @property
    def _comment(self) -> str:
        comm = self.handle.get("COMM::XXX", None)
        if comm is not None and len(comm.text) > 0:
            return comm.text[0]
        return self._get_first("COMM:ID3v1 Comment:eng")

    @_comment.setter
    def _comment(self, comment: str) -> None:
        self.handle.tags.delall("COMM")
        comm = id3.COMM(desc="ID3v1 Comment", lang="eng", text=comment)
        self.handle.tags.add(comm)

    @property
    def _description(self) -> str:
        return " ".join([self._get_first("description"), self._get_first("comment")]).strip()

    @_description.setter
    def _description(self, description: str) -> None:
        self.handle.tags["description"] = description
        self.handle.tags["comment"] = description

    @property
    def track(self) -> None | int:
        track_tag = "tracknumber" if self.extension == ".flac" else "TRCK"
        track = self._get_first(track_tag)
        try:
            if "/" in track:
                track = track.split("/", maxsplit=1)[0]
            n = int(track)
            if n < 0:
                return -1
            if n > 2**31 - 1:
                logger.warning(f"{self} : invalid track number {n}")
                return None
            return n
        except ValueError:
            return None

    @track.setter
    def track(self, number: int) -> None:
        if self.extension == ".flac":
            self.handle.tags["tracknumber"] = str(number)
        else:
            self.handle.tags.delall("TRCK")
            trck = id3.TRCK(text=str(number))
            self.handle.tags.add(trck)

    @property
    def keywords(self) -> set[str]:
        if self.extension == ".mp3":
            return set(mysplit(self._comment, " "))
        if self.extension == ".flac":
            if self._comment and not self._description:
                logger.warning(f"{self} : fixing flac keywords with mp3 comment")
                self._description = self._comment
            return set(mysplit(self._description, " "))
        return set()

    @keywords.setter
    def keywords(self, keywords: set[str]) -> None:
        if self.extension == ".mp3":
            logger.info(f"{self} : new mp3 keywords : {keywords}")
            self._comment = " ".join(keywords)
        elif self.extension == ".flac":
            logger.info(f"{self} : new flac keywords : {keywords}")
            self._description = " ".join(keywords)
        else:
            self.err(f"{self} : unknown extension {self.extension}")

    def add_keywords(self, keywords: set[str]) -> bool:
        self.keywords = self.keywords.union(keywords)
        logger.info(f"{self} : adding {keywords}, new keywords {self.keywords}")
        return self.save()

    def delete_keywords(self, keywords: set[str]) -> bool:
        new_keywords = self.keywords - set(keywords)
        logger.info(f"{self} : deleting {keywords}, new keywords {new_keywords}")
        self.keywords = new_keywords
        return self.save()

    def to_mp3(self, destination: Path, flat: bool = False) -> Self | None:
        if not flat and Issue.INVALID_PATH in self.issues:
            self.err(f"{self} does not have a canonic path like : {self.canonic_artist_album_filename}")
            return None

        if flat:
            mp3_path = destination / f"{self.flat_title}.mp3"
        else:
            mp3_path = destination / self.artist / self.album / (self.canonic_title + ".mp3")

        if mp3_path.exists():
            logger.info(f"{mp3_path} already exists, overwriting only tags")
            mp3_file = self.from_path(folder=destination, path=mp3_path)
            if not mp3_file:
                self.err("unable to load existing mp3 file")
                return None

            if self.track is not None:
                mp3_file.track = self.track
            mp3_file.album = self.album
            mp3_file.title = self.title
            mp3_file.artist = self.artist
            mp3_file.genre = self.genre
            mp3_file.rating = self.rating
            mp3_file.keywords = self.keywords
            if not mp3_file.save():
                return None
            return mp3_file

        if self.extension == ".mp3":
            self.warn(f"{self} is already an MP3")
            _ = shutil.copyfile(self.path, str(mp3_path))
            if self.dry:
                return None
            mp3_file = self.from_path(folder=destination, path=mp3_path)
            return mp3_file

        logger.debug(f"{self} convert destination : {mp3_path}")
        if self.dry:
            return None
        mp3_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            flac_audio = AudioSegment.from_file(self.path, "flac")
            mp3_export = flac_audio.export(
                mp3_path,
                format="mp3",
                bitrate="256k",
            )
            mp3_export.close()
            if not (mp3_file := self.from_path(folder=destination, path=mp3_path)):
                self.err("unable to load freshly converted mp3 file")
                return None

            # rewrite some metadatas
            if self.track is not None:
                mp3_file.track = self.track
            mp3_file.album = self.album
            mp3_file.title = self.title
            mp3_file.genre = self.genre
            mp3_file.artist = self.artist
            mp3_file.rating = self.rating
            mp3_file.keywords = self.keywords
            if mp3_file.save():
                return mp3_file
        except Exception as error:
            mp3_path.unlink()
            self.err(f"{self} : unable to convert to mp3", error=error)
        return None

    async def shazam(self) -> Any:
        shazam = Shazam()
        return await shazam.recognize(self.path)

    def fingerprint(self, api_key: str) -> str | None:
        try:
            ids = acoustid.match(api_key, self.path)
            for score, recording_id, title, artist in ids:
                logger.info(f"{self} score : {score} | recording_id : {recording_id} | title : {title} | artist : {artist}")
                return str(recording_id)
        except acoustid.WebServiceError:
            self.err(f"{self} : unable to get fingerprint")
        return None

    def fix(self) -> bool:
        for issue in self.issues:
            match issue:  # noqa
                case Issue.NO_ARTIST:
                    self.success(f"{self} : give new artist (old '{self.artist}')")
                    self.artist = input()
                    if not self.save():
                        return False
                case Issue.NO_TITLE:
                    self.success(f"{self} : give new title (old '{self.title}')")
                    self.title = input()
                    if not self.save():
                        return False
                case Issue.NO_GENRE:
                    self.success(f"{self} : give new genre (old '{self.genre}')")
                    self.genre = input()
                    if not self.save():
                        return False
                case Issue.NO_ALBUM:
                    self.success(f"{self} : give new album (old '{self.album}')")
                    self.album = input()
                    if not self.save():
                        return False
                case Issue.NO_RATING:
                    if not self.dry:
                        self.rating = 0.0
                    if not self.save():
                        return False
                case Issue.NO_TRACK:
                    if not self.dry:
                        self.track = 0
                    if not self.save():
                        return False
                case Issue.INVALID_COMMENT:
                    logger.info(f"{self} : fixing comment")
                    if self.extension == ".flac" and self._comment and not self._description and not self.dry:
                        self._description = ""
                    if self.extension == ".mp3" and self._description and not self._comment and not self.dry:
                        self._comment = ""
                    if not self.save():
                        return False
                case Issue.INVALID_TITLE:
                    logger.info(f"{self} : {self.title} => {self.canonic_title}")
                    if not self.dry:
                        self.title = self.canonic_title
                    if not self.save():
                        return False
                case Issue.INVALID_PATH:
                    logger.info(f"{self} : moving from {self.path} to {self.canonic_path}")
                    if not self.dry:
                        self.canonic_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(self.path, self.canonic_path)
                        self.handle = MutagenFile(self.canonic_path)
        return self.save()

    def save(self) -> bool:
        try:
            if self.dry:
                return True
            self.handle.save()
            return True
        except MutagenError as error:
            self.err(f"{self} : unable to save", error=error)
        return False
