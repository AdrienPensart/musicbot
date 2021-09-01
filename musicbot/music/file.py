from pathlib import Path, PurePath
from typing import Any, Set, Optional, List, Dict, Iterable
import logging
import json
import acoustid  # type: ignore
import mutagen  # type: ignore
from slugify import slugify
from pydub import AudioSegment  # type: ignore
from click_skeleton.helpers import mysplit
from musicbot.object import MusicbotObject
from musicbot.helpers import parse_graphql, current_user, public_ip

logger = logging.getLogger(__name__)
DEFAULT_ACOUSTID_API_KEY: Optional[str] = None

output_types = ["list", "json"]

default_checks = [
    'keywords',
    'strict_title',
    'title',
    'path',
    'genre',
    'album',
    'artist',
    'rating',
    'number'
]

STOPWORDS = [
    'the',
    'remaster',
    'standard',
    'remastered',
    'bonus',
    'cut',
    'part',
    'edition',
    'version',
    'mix',
    'deluxe',
    'edit',
    'album',
    'lp',
    'ep',
    'uk',
    'track',
    'expanded',
    'single',
    'volume',
    'vol',
    'legacy',
    'special',
] + list(map(str, range(1900, 2020)))

REPLACEMENTS = [['praxis', 'buckethead'], ['lawson-rollins', 'buckethead']]

DEFAULT_CHECKS = [
    'no-title',
    'no-artist',
    'no-album',
    'no-genre',
    'no-rating',
    'no-tracknumber',
    'invalid-title',
    'invalid-comment',
    'invalid-path',
]


class File:
    def __init__(self, path):
        path = path.resolve()
        self.handle = mutagen.File(path)
        self.inconsistencies: Set[str] = set()

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
        if self.number == -1:
            self.inconsistencies.add("no-tracknumber")
        if self.extension == '.flac' and self._comment and not self._description:
            self.inconsistencies.add('invalid-comment')
        if self.extension == '.mp3' and self._description and not self._comment:
            self.inconsistencies.add('invalid-comment')
        if self.number not in (-1, 0) and self.title != self.canonic_title:
            logger.debug(f"{self} : invalid-title, '{self.title}' should be '{self.canonic_title}'")
            self.inconsistencies.add("invalid-title")
        if self.number not in (-1, 0) and not str(self.path).endswith(str(self.canonic_artist_album_filename)):
            logger.debug(f"{self} : invalid-path, must have a number and should end with '{self.canonic_artist_album_filename}'")
            self.inconsistencies.add("invalid-path")

    def __repr__(self) -> str:
        return str(self.path)

    def as_dict(self) -> Dict[str, Any]:  # pylint: disable=unsubscriptable-object
        return {
            'title': self.title,
            'album': self.album,
            'genre': self.genre,
            'artist': self.artist,
            'number': self.number,
            'rating': self.rating,
            'duration': self.duration,
            'keywords': self.keywords,
        }

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

    def to_graphql(self) -> str:
        return ", ".join([f'{k}: {json.dumps(v)}' for k, v in self.as_dict().items()])

    def to_json(self) -> str:
        return json.dumps(self.as_dict())

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
        return slugify(f"""{self.artist}-{self.title}""", stopwords=STOPWORDS, replacements=REPLACEMENTS)  # type: ignore

    def _get_first(self, tag: str, default: str = '') -> str:
        if tag not in self.handle:
            return default
        for item in self.handle[tag]:
            return str(item)
        return default

    @property
    def duration(self) -> int:
        return int(self.handle.info.length)

    @property
    def size(self) -> int:
        return Path(self.path).stat().st_size

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
        return f"{str(self.number).zfill(2)} - {self.title}"

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
            return self._get_first('genre')
        return self._get_first('TCON')

    @genre.setter
    def genre(self, genre: str) -> None:
        if self.extension == '.flac':
            self.handle.tags['genre'] = genre
        else:
            self.handle.tags.add(mutagen.id3.TCON(text=genre))

    @property
    def rating(self) -> float:
        if self.extension == '.flac':
            s = self._get_first('fmps_rating')
        else:
            s = self._get_first('TXXX:FMPS_Rating')
        try:
            n = float(s)
            if n < 0.0:
                return 0.0
            return n * 5.0
        except ValueError:
            return -1

    @rating.setter
    def rating(self, rating: float) -> None:
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
    def number(self) -> int:
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

    @number.setter
    def number(self, number: int) -> None:
        if self.extension == '.flac':
            self.handle.tags['tracknumber'] = str(number)
        else:
            self.handle.tags.delall('TRCK')
            self.handle.tags.add(mutagen.id3.TRCK(text=str(number)))

    @property
    def keywords(self) -> List[str]:
        if self.extension == '.mp3':
            return mysplit(self._comment, ' ')
        if self.extension == '.flac':
            if self._comment and not self._description:
                logger.warning(f'{self} : fixing flac keywords with mp3 comment')
                self._description = self._comment
            return mysplit(self._description, ' ')
        return []

    @keywords.setter
    def keywords(self, keywords: Iterable[str]) -> None:
        if self.extension == '.mp3':
            logger.info(f'{self} : new mp3 keywords : {keywords}')
            self._comment = ' '.join(keywords)
        elif self.extension == '.flac':
            logger.info(f'{self} : new flac keywords : {keywords}')
            self._description = ' '.join(keywords)
        else:
            logger.error(f'{self} : unknown extension {self.extension}')

    def add_keywords(self, keywords: Iterable[str]) -> bool:
        self.keywords = list(set(self.keywords).union(set(keywords)))
        logger.info(f'{self} : adding {keywords}, new keywords {self.keywords}')
        return self.save()

    def delete_keywords(self, keywords: Iterable[str]) -> bool:
        new_keywords = list(set(self.keywords) - set(keywords))
        logger.info(f'{self} : deleting {keywords}, new keywords {new_keywords}')
        self.keywords = new_keywords
        return self.save()

    def to_mp3(self, destination: Path, flat: Optional[bool] = False) -> bool:
        if self.extension != '.flac':
            logger.error(f"{self} is not a flac file")
            return False

        if not flat and 'invalid-path' in self.inconsistencies:
            logger.error(f"{self} does not have a canonic path like : {self.canonic_artist_album_filename}")
            return False

        if flat:
            mp3_path = destination / f'{self.flat_title}.mp3'
        else:
            mp3_path = destination / self.artist / self.album / (self.canonic_title + '.mp3')

        if mp3_path.exists():
            logger.info(f"{mp3_path} already exists, overwriting only tags")
            f = File(path=mp3_path)
            f.number = self.number
            f.album = self.album
            f.title = self.title
            f.artist = self.artist
            return f.save()

        logger.debug(f"{self} convert destination : {mp3_path}")
        if not MusicbotObject.dry:
            mp3_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                flac_audio = AudioSegment.from_file(self.path, "flac")
                mp3_file = flac_audio.export(
                    mp3_path,
                    format="mp3",
                    bitrate="256k",
                )
                mp3_file.close()
                f = File(mp3_path)
                f.number = self.number
                f.album = self.album
                f.title = self.title
                f.artist = self.artist
                return f.save()
            except Exception:
                mp3_path.unlink()
                raise
        return False

    def upsert_mutation(self, user_id: int, sftp=False, http=False, local=True, spotify=False, youtube=False, operation: Optional[str] = None) -> str:
        paths = []
        if local:
            paths.append(str(self.path))
        if sftp and self.sftp_path:
            paths.append(self.sftp_path)
        if http and self.http_path:
            paths.append(self.http_path)
        if youtube and self.youtube_path:
            paths.append(self.youtube_path)
        if spotify and self.spotify_path:
            paths.append(self.spotify_path)

        operation = operation if operation is not None else ""
        mutation = f'''
        mutation {operation} {{
            upsertMusic(
                where: {{
                    title: {json.dumps(self.title)}
                    album: {json.dumps(self.album)}
                    artist: {json.dumps(self.artist)}
                    userId: {user_id}
                }}
                input: {{
                    music: {{
                        title: {json.dumps(self.title)}
                        album: {json.dumps(self.album)}
                        artist: {json.dumps(self.artist)}
                        duration: {self.duration}
                        genre: {json.dumps(self.genre)}
                        keywords: {json.dumps(self.keywords)}
                        number: {self.number}
                        rating: {self.rating}
                        links: {json.dumps(paths)}
                    }}
                }}
            )
            {{
                clientMutationId
            }}
        }}
        '''
        parse_graphql(mutation)
        return mutation

    def fingerprint(self, api_key: str) -> str:
        ids = acoustid.match(api_key, self.path)
        for score, recording_id, title, artist in ids:
            logger.info(f"{self} score : {score} | recording_id : {recording_id} | title : {title} | artist : {artist}")
            return str(recording_id)
        logger.info(f'{self} : fingerprint cannot be detected')
        return ''

    def fix(self, checks: Optional[Iterable[str]] = None) -> bool:
        checks = checks if checks is not None else DEFAULT_CHECKS
        if 'no-rating' in checks:
            self.rating = 0.0
            self.inconsistencies.remove('no-rating')
        if 'no-tracknumber' in checks:
            self.number = 0
            self.inconsistencies.remove('no-tracknumber')
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
            if not MusicbotObject.dry:
                self.handle.save()
            return True
        except mutagen.MutagenError as e:
            logger.error(e)
        return False

    def close(self) -> None:
        self.handle.close()
