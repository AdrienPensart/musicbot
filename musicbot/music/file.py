import logging
from pathlib import Path, PurePath
import json
import os
from typing import Any, Optional, List, Dict, Iterable, Iterator
import acoustid  # type: ignore
import mutagen  # type: ignore
from gql import gql  # type: ignore
from slugify import slugify
from pydub import AudioSegment  # type: ignore
from click_skeleton.helpers import mysplit
from musicbot.object import MusicbotObject
from musicbot.exceptions import QuerySyntaxError
from musicbot.helpers import current_user, public_ip
from musicbot.music.helpers import ensure

logger = logging.getLogger(__name__)
DEFAULT_ACOUSTID_API_KEY: Optional[str] = None

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
supported_formats = ["mp3", "flac"]


# pylint: disable-msg=unsupported-membership-test
# pylint: disable-msg=unsubscriptable-object
# pylint: disable-msg=unsupported-assignment-operation
class File:
    def __init__(self, path: str, folder: Optional[str] = None, youtube_link: Optional[str] = None, spotify_link: Optional[str] = None):
        self.path = path
        self.folder = folder if folder is not None else ''
        self.youtube_link = youtube_link if youtube_link is not None else ''
        self.spotify_link = spotify_link if spotify_link is not None else ''
        self.handle = mutagen.File(self.path)
        self.inconsistencies = []
        if not self.title:
            self.inconsistencies.append("no-title")
        if self.genre == '':
            self.inconsistencies.append("no-genre")
        if self.album == '':
            self.inconsistencies.append("no-album")
        if self.artist == '':
            self.inconsistencies.append("no-artist")
        if self.rating == -1:
            self.inconsistencies.append("no-rating")
        if self.number == -1:
            self.inconsistencies.append("no-tracknumber")
        if self.extension == '.flac' and self._comment and not self._description:
            self.inconsistencies.append('invalid-comment')
        if self.extension == '.mp3' and self._description and not self._comment:
            self.inconsistencies.append('invalid-comment')
        if self.number not in (-1, 0) and self.title != self.canonic_title:
            logger.debug(f"invalid-title, '{self.title}' should be '{self.canonic_title}'")
            self.inconsistencies.append("invalid-title")
        if self.number not in (-1, 0) and not self.path.endswith(self.canonic_path):
            logger.debug(f"invalid-path, '{self.path}' should be '{self.canonic_path}'")
            self.inconsistencies.append("invalid-path")

    def __repr__(self) -> str:
        return self.path

    def __iter__(self) -> Iterator[Any]:
        yield from self.as_dict().items()

    def close(self) -> None:
        self.handle.close()

    def to_mp3(self, folder: Optional[str] = None, flat: Optional[bool] = False) -> bool:
        folder = folder if folder is not None else self.folder

        if self.extension != '.flac':
            logger.error(f"{self} is not a flac file")
            return False

        if not flat and 'invalid-path' in self.inconsistencies:
            logger.error(f"{self} does not have a canonic path like : {self.canonic_artist_album_filename}")
            return False

        if flat:
            mp3_path = os.path.join(folder, f'{self.flat_title}.mp3')
        else:
            mp3_path = os.path.join(folder, self.artist, self.album, self.canonic_title + '.mp3')

        if os.path.exists(mp3_path):
            logger.info(f"{mp3_path} already exists, overwriting only tags")
            f = File(mp3_path)
            f.number = self.number
            f.album = self.album
            f.title = self.title
            f.artist = self.artist
            f.save()
            return False
        logger.debug(f"{self} convert destination : {mp3_path}")
        if not MusicbotObject.dry:
            ensure(mp3_path)
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
                f.save()
            except Exception:
                os.remove(mp3_path)
                raise
        return True

    def create_mutation(self, operationName=None) -> str:
        operationName = operationName if operationName is not None else ""
        mutation = f'''
        mutation {operationName} {{
            createMusic(
                input: {{
                    music: {{
                        title: {json.dumps(self.title)},
                        album: {json.dumps(self.album)},
                        artist: {json.dumps(self.artist)},
                        duration: {self.duration},
                        genre: {json.dumps(self.genre)},
                        keywords: {json.dumps(self.keywords)},
                        number: {self.number},
                        rating: {self.rating},
                        linksUsingId: {{
                            create: [
                                {{
                                    url: "{self.path}"
                                }},
                                {{
                                    url: "{self.ssh_path}"
                                }},
                            ]
                        }}
                    }}
                }}
            )
            {{
                clientMutationId
            }}
        }}
        '''
        try:
            gql(mutation)
        except Exception as e:
            raise QuerySyntaxError(f"{self} : bad mutation : {mutation}") from e
        return mutation

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
    def ssh_path(self) -> str:
        return f"ssh://{current_user()}@{public_ip()}:{self.path}"

    @property
    def extension(self) -> str:
        return Path(self.path).suffix

    def to_graphql(self) -> str:
        return ", ".join([f'{k}: {json.dumps(v)}' for k, v in self.as_dict().items()])

    def to_json(self) -> str:
        return json.dumps(self.as_dict())

    @property
    def canonic_path(self) -> str:
        return str(PurePath(self.folder, self.canonic_artist_album_filename))

    @property
    def canonic_artist_album_filename(self) -> str:
        return str(PurePath(self.artist, self.album, self.canonic_filename))

    @property
    def filename(self) -> str:
        return Path(self.path).name

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

    @property
    def youtube(self) -> str:
        return self.youtube_link

    @property
    def spotify(self) -> str:
        return self.spotify_link

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
        if 'invalid-path' in checks:
            logger.info(f"{self} : {self.path} => {self.canonic_path}")
            if not MusicbotObject.dry:
                ensure(self.canonic_path)
                path = Path(self.path)
                path.replace(self.canonic_path)
                self.path = self.canonic_path
                self.handle = mutagen.File(self.path)
                self.inconsistencies.remove('invalid-path')
        return self.save()

    def save(self) -> bool:
        try:
            if not MusicbotObject.dry:
                self.handle.save()
            return True
        except mutagen.MutagenError as e:
            logger.error(e)
        return False
