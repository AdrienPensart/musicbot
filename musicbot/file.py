import logging
from functools import cached_property
from pathlib import Path, PurePath
from typing import Iterable, Optional

import acoustid  # type: ignore
import mutagen  # type: ignore
from attr import define
from click_skeleton.helpers import mysplit
from pydub import AudioSegment  # type: ignore
from slugify import slugify

from musicbot.defaults import (
    DEFAULT_CHECKS,
    DEFAULT_MAX_RATING,
    DEFAULT_MIN_RATING,
    RATING_CHOICES,
    REPLACEMENTS,
    STOPWORDS,
    STORED_RATING_CHOICES
)
from musicbot.helpers import current_user, public_ip
from musicbot.link_options import DEFAULT_LINK_OPTIONS, LinkOptions
from musicbot.object import MusicbotObject
from musicbot.music import Music
from musicbot.exceptions import MusicbotError

logger = logging.getLogger(__name__)


@define(repr=False)
class File(MusicbotObject):
    handle: mutagen.File
    inconsistencies: set[str] = set()

    def __attrs_post_init__(self) -> None:
        if not self.title:
            self.inconsistencies.add("no-title")
        if not self.genre:
            self.inconsistencies.add("no-genre")
        if not self.album:
            self.inconsistencies.add("no-album")
        if not self.artist:
            self.inconsistencies.add("no-artist")
        if self.rating == -1:
            self.inconsistencies.add("no-rating")
        if self.track == -1:
            self.inconsistencies.add("no-track")
        if self.extension == '.flac' and self._comment and not self._description:
            self.inconsistencies.add('invalid-comment')
        if self.extension == '.mp3' and self._description and not self._comment:
            self.inconsistencies.add('invalid-comment')
        if self.track not in (-1, 0) and self.title != self.canonic_title:
            logger.debug(f"{self} : invalid-title, '{self.title}' should be '{self.canonic_title}'")
            self.inconsistencies.add("invalid-title")
        if self.track not in (-1, 0) and not str(self.path).endswith(str(self.canonic_artist_album_filename)):
            logger.debug(f"{self} : invalid-path, must have a track and should end with '{self.canonic_artist_album_filename}'")
            self.inconsistencies.add("invalid-path")

    @classmethod
    def from_path(cls, path: Path) -> "File":
        return cls(
            handle=mutagen.File(path.resolve())
        )

    def __repr__(self) -> str:
        return str(self.path)

    def to_music(
        self,
        link_options: LinkOptions = DEFAULT_LINK_OPTIONS
    ) -> Music:
        return Music(
            title=self.title,
            size=self.size,
            album=self.album,
            artist=self.artist,
            genre=self.genre,
            length=self.length,
            track=self.track,
            rating=self.rating,
            keywords=list(sorted(self.keywords)),
            links=list(sorted(self.links(link_options))),
        )

    def set_tags(
        self,
        title: str | None = None,
        artist: str | None = None,
        album: str | None = None,
        genre: str | None = None,
        keywords: list[str] | None = None,
        rating: float | None = None,
        track: int | None = None,
    ) -> None:
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
        self.save()

    @cached_property
    def size(self) -> int:
        return self.path.stat().st_size

    @property
    def path(self) -> Path:
        return Path(self.handle.filename)

    @property
    def http_path(self) -> str:
        return f"http://{public_ip()}/{self.canonic_artist_album_filename}"

    @property
    def sftp_path(self) -> str:
        return f"sftp://{current_user()}@{public_ip()}:{self.path}"

    @property
    def youtube_path(self) -> str:
        return ''

    @property
    def spotify_path(self) -> str:
        return ''

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
    def canonic_filename(self) -> str:
        return f"{self.canonic_title}{self.extension}"

    @property
    def flat_title(self) -> str:
        return f'{self.artist} - {self.album} - {self.canonic_title}'

    @property
    def flat_filename(self) -> str:
        return f'{self.artist} - {self.album} - {self.canonic_title}{self.extension}'

    @property
    def slug(self) -> str:
        return slugify(f"""{self.artist}-{self.title}""", stopwords=STOPWORDS, replacements=REPLACEMENTS)

    def _get_first(self, tag: str, default: str = '') -> str:
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
        if self.extension == '.flac':
            return self._get_first('title')
        return self._get_first('TIT2')

    @title.setter
    def title(self, title: str) -> None:
        if self.extension == '.flac':
            self.handle.tags['title'] = title
        else:
            self.handle.tags.add(mutagen.id3.TIT2(text=title))

    @property
    def canonic_title(self) -> str:
        return f"{str(self.track).zfill(2)} - {self.title}"

    @property
    def album(self) -> str:
        if self.extension == '.flac':
            return self._get_first('album')
        return self._get_first('TALB')

    @album.setter
    def album(self, album: str) -> None:
        if self.extension == '.flac':
            self.handle.tags['album'] = album
        else:
            self.handle.tags.add(mutagen.id3.TALB(text=album))

    @property
    def artist(self) -> str:
        if self.extension == '.flac':
            return self._get_first('artist')
        return self._get_first('TPE1')

    @artist.setter
    def artist(self, artist: str) -> None:
        if self.extension == '.flac':
            self.handle.tags['artist'] = artist
        else:
            self.handle.tags.add(mutagen.id3.TPE1(text=artist))

    @property
    def genre(self) -> str:
        if self.extension == '.flac':
            genre = self._get_first('genre')
        else:
            genre = self._get_first('TCON')
        if not genre:
            logger.debug(f"{self} : no genre set")
        return genre

    @genre.setter
    def genre(self, genre: str) -> None:
        if self.extension == '.flac':
            self.handle.tags['genre'] = genre
        else:
            self.handle.tags.add(mutagen.id3.TCON(text=genre))

    @property
    def rating(self) -> float:
        if self.extension == '.flac':
            rating_str = self._get_first('fmps_rating')
        else:
            rating_str = self._get_first('TXXX:FMPS_Rating')
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
            self.err(f"{self} : cannot convert rating to float : '{rating_str}'", only_once=True)
            return 0.0

    @rating.setter
    def rating(self, rating: float) -> None:
        if rating not in RATING_CHOICES:
            self.err(f"{self} : tried to set a bad rating : {rating}")
            return
        rating /= 5.0
        if self.extension == '.flac':
            self.handle['fmps_rating'] = str(rating)
        else:
            self.handle.tags.add(mutagen.id3.TXXX(desc='FMPS_Rating', text=str(rating)))

    @property
    def _comment(self) -> str:
        return self._get_first('COMM:ID3v1 Comment:eng')

    @_comment.setter
    def _comment(self, comment: str) -> None:
        self.handle.tags.delall('COMM')
        self.handle.tags.add(mutagen.id3.COMM(desc='ID3v1 Comment', lang='eng', text=comment))

    @property
    def _description(self) -> str:
        return self._get_first('description')

    @_description.setter
    def _description(self, description: str) -> None:
        self.handle.tags['description'] = description

    @property
    def track(self) -> int:
        if self.extension == '.flac':
            s = self._get_first('tracknumber')
        else:
            s = self._get_first('TRCK')
        try:
            if '/' in s:
                s = s.split('/', maxsplit=1)[0]
            n = int(s)
            if n < 0:
                return -1
            if n > 2 ** 31 - 1:
                logger.warning(f"{self} : invalid track number {n}")
                return 0
            return n
        except ValueError:
            return -1

    @track.setter
    def track(self, number: int) -> None:
        if self.extension == '.flac':
            self.handle.tags['tracknumber'] = str(number)
        else:
            self.handle.tags.delall('TRCK')
            self.handle.tags.add(mutagen.id3.TRCK(text=str(number)))

    @property
    def keywords(self) -> set[str]:
        if self.extension == '.mp3':
            return set(mysplit(self._comment, ' '))
        if self.extension == '.flac':
            if self._comment and not self._description:
                logger.warning(f'{self} : fixing flac keywords with mp3 comment')
                self._description = self._comment
            return set(mysplit(self._description, ' '))
        return set()

    @keywords.setter
    def keywords(self, keywords: Iterable[str]) -> None:
        if self.extension == '.mp3':
            logger.info(f'{self} : new mp3 keywords : {keywords}')
            self._comment = ' '.join(keywords)
        elif self.extension == '.flac':
            logger.info(f'{self} : new flac keywords : {keywords}')
            self._description = ' '.join(keywords)
        else:
            self.err(f'{self} : unknown extension {self.extension}')

    def add_keywords(self, keywords: set[str]) -> bool:
        self.keywords = self.keywords.union(keywords)
        logger.info(f'{self} : adding {keywords}, new keywords {self.keywords}')
        return self.save()

    def delete_keywords(self, keywords: set[str]) -> bool:
        new_keywords = self.keywords - set(keywords)
        logger.info(f'{self} : deleting {keywords}, new keywords {new_keywords}')
        self.keywords = new_keywords
        return self.save()

    def to_mp3(self, destination: Path, flat: bool = False) -> Optional["File"]:
        if self.extension != '.flac':
            self.err(f"{self} is not a flac file")
            return None

        if not flat and 'invalid-path' in self.inconsistencies:
            self.err(f"{self} does not have a canonic path like : {self.canonic_artist_album_filename}")
            return None

        if flat:
            mp3_path = destination / f'{self.flat_title}.mp3'
        else:
            mp3_path = destination / self.artist / self.album / (self.canonic_title + '.mp3')

        if mp3_path.exists():
            logger.info(f"{mp3_path} already exists, overwriting only tags")
            mp3_file = File.from_path(path=mp3_path)
            mp3_file.track = self.track
            mp3_file.album = self.album
            mp3_file.title = self.title
            mp3_file.artist = self.artist
            mp3_file.save()
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
            mp3_file = File.from_path(mp3_path)
            mp3_file.track = self.track

            # rewrite some metadatas
            mp3_file.album = self.album
            mp3_file.title = self.title
            mp3_file.artist = self.artist
            if mp3_file.save():
                return mp3_file
        except Exception as e:
            mp3_path.unlink()
            raise MusicbotError(f"{self} : unable to convert to mp3") from e
        return None

    def fingerprint(self, api_key: str) -> str:
        ids = acoustid.match(api_key, self.path)
        for score, recording_id, title, artist in ids:
            logger.info(f"{self} score : {score} | recording_id : {recording_id} | title : {title} | artist : {artist}")
            return str(recording_id)
        logger.info(f'{self} : fingerprint cannot be detected')
        return ''

    def fix(self, checks: Iterable[str] | None = None) -> bool:
        checks = checks if checks is not None else DEFAULT_CHECKS
        if 'no-rating' in checks:
            self.rating = 0.0
            self.inconsistencies.remove('no-rating')
        if 'no-track' in checks:
            self.track = 0
            self.inconsistencies.remove('no-track')
        if 'invalid-comment' in checks:
            if self.extension == '.flac' and self._comment and not self._description:
                self._description = ''
            if self.extension == '.mp3' and self._description and not self._comment:
                self._comment = ''
            self.inconsistencies.remove('invalid-comment')
        if 'invalid-title' in checks:
            logger.info(f"{self} : {self.title} => {self.canonic_title}")
            self.title = self.canonic_title
            self.inconsistencies.remove('invalid-title')
        return self.save()

    def save(self) -> bool:
        try:
            if self.dry:
                return True
            self.handle.save()
        except mutagen.MutagenError as e:
            self.err(e)
        return False

    def close(self) -> None:
        self.handle.close()

    def links(self, link_options: LinkOptions = DEFAULT_LINK_OPTIONS) -> set[str]:
        links = set()
        if link_options.local:
            links.add(str(self.path))
        if link_options.sftp and self.sftp_path:
            links.add(self.sftp_path)
        if link_options.http and self.http_path:
            links.add(self.http_path)
        if link_options.youtube and self.youtube_path:
            links.add(self.youtube_path)
        if link_options.spotify and self.spotify_path:
            links.add(self.spotify_path)
        return links
