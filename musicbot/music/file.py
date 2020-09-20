import logging
import pathlib
import json
import os
from typing import Any, Optional, List, Dict, Iterable, Iterator
import click
import acoustid  # type: ignore
import mutagen  # type: ignore
from pydub import AudioSegment  # type: ignore
from click_option_group import optgroup  # type: ignore
from click_skeleton.helpers import mysplit
from .helpers import ensure


logger = logging.getLogger(__name__)

music_options_group = [optgroup.group('Music options')]
keywords_option = [optgroup.option('--keywords', help='Keywords', multiple=True)]
artist_option = [optgroup.option('--artist', help='Artist', default=None)]
album_option = [optgroup.option('--album', help='Album', default=None)]
title_option = [optgroup.option('--title', help='Title', default=None)]
genre_option = [optgroup.option('--genre', help='Genre', default=None)]
number_option = [optgroup.option('--number', help='Track number', default=None)]
rating_option = [optgroup.option('--rating', help='Rating', default=None)]

keywords_argument = [
    click.argument(
        'keywords',
        nargs=-1,
    ),
]

options =\
    music_options_group +\
    keywords_option +\
    artist_option +\
    album_option +\
    title_option +\
    genre_option +\
    number_option +\
    rating_option

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
path_argument = [
    click.argument(
        'path',
        type=click.Path(exists=True, dir_okay=False),
    ),
]
folder_option = [
    click.option(
        '--folder',
        help="Destination folder",
        type=click.Path(exists=True, file_okay=False),
    ),
]
folder_argument = [
    click.argument(
        'folder',
        type=click.Path(exists=True, file_okay=False),
    ),
]
checks_options = [
    optgroup.group('Check options'),
    optgroup.option(
        '--checks',
        help='Consistency tests',
        multiple=True,
        default=DEFAULT_CHECKS,
        show_default=True,
        type=click.Choice(DEFAULT_CHECKS),
    ),
    optgroup.option(
        '--fix',
        help="Fix musics",
        is_flag=True,
    ),
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
            logger.info(f"invalid-title, '{self.title}' should be '{self.canonic_title}'")
            self.inconsistencies.append("invalid-title")
        if self.number not in (-1, 0) and not self.path.endswith(self.canonic_path):
            logger.info(f"invalid-path, '{self.path}' should be '{self.canonic_path}'")
            self.inconsistencies.append("invalid-path")

    def __repr__(self) -> str:
        return self.path

    def __iter__(self) -> Iterator[Any]:
        yield from self.as_dict().items()

    def close(self) -> None:
        self.handle.close()

    def to_mp3(self, folder: Optional[str] = None, dry: Optional[bool] = None) -> bool:
        dry = dry if dry is not None else False
        folder = folder if folder is not None else self.folder

        if self.extension != '.flac':
            logger.error(f"{self} is not a flac file")
            return False
        if 'invalid-path' in self.inconsistencies:
            logger.error(f"{self} does not have a canonic path like : {self.canonic_artist_album_filename}")
            return False

        mp3_path = os.path.join(folder, self.artist, self.album, self.canonic_title + '.mp3')
        if os.path.exists(mp3_path):
            logger.info(f"{mp3_path} already exists, not overwriting")
            return False
        logger.debug(f"{self} convert destination : {mp3_path}")
        if not dry:
            ensure(mp3_path)
            flac_audio = AudioSegment.from_file(self.path, "flac")
            flac_audio.export(mp3_path, format="mp3")
        return True

    def as_dict(self) -> Dict[str, Any]:  # pylint: disable=unsubscriptable-object
        return {
            'title': self.title,
            'album': self.album,
            'genre': self.genre,
            'artist': self.artist,
            'folder': self.folder,
            'youtube': self.youtube,
            'spotify': self.spotify,
            'number': self.number,
            'path': self.path,
            'rating': self.rating,
            'duration': self.duration,
            'size': self.size,
            'keywords': self.keywords,
        }

    @property
    def extension(self) -> str:
        return pathlib.Path(self.path).suffix

    def to_graphql(self) -> str:
        return ", ".join([f'{k}: {json.dumps(v)}' for k, v in self.as_dict().items()])

    def to_json(self) -> str:
        return json.dumps(self.as_dict())

    @property
    def canonic_path(self) -> str:
        return str(pathlib.PurePath(self.folder, self.canonic_artist_album_filename))

    @property
    def canonic_artist_album_filename(self) -> str:
        return str(pathlib.PurePath(self.artist, self.album, self.canonic_filename))

    @property
    def filename(self) -> str:
        return os.path.basename(self.path)

    @property
    def canonic_filename(self) -> str:
        return f"{self.canonic_title}{self.extension}"

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
        return os.path.getsize(self.path)

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
        self.handle.tags.add(mutagen.id3.COMM(desc='ID3v1 Comment:eng', text=str(comment)))

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
                s = s.split('/')[0]
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
            logger.info(f'{self} : mp3 {keywords}')
            self._comment = ' '.join(keywords)
        elif self.extension == '.flac':
            logger.info(f'{self} : flac {keywords}')
            self._description = ' '.join(keywords)
        else:
            logger.error(f'{self} : unknown extension {self.extension}')

    def add_keywords(self, keywords: Iterable[str], dry: Optional[bool] = None) -> bool:
        dry = dry if dry is not None else False
        tags = self.keywords
        for k in keywords:
            if k not in tags:
                logger.info(f'{self} : new keyword {k}')
                tags.append(k)
        if set(self.keywords) != set(tags):
            self.keywords = tags
            print(self.keywords)
            print(tags)
            logger.info(f'{self} : new keywords {self.keywords}')
            return self.save(dry)
        return False

    def delete_keywords(self, keywords: Iterable[str], dry: Optional[bool] = None) -> bool:
        dry = dry if dry is not None else False
        tags = self.keywords
        for k in keywords:
            if k in tags:
                logger.info(f'{self} : new keyword {k}')
                tags.remove(k)
        if set(self.keywords) != set(tags):
            self.keywords = tags
            logger.info(f'{self} : new keywords {self.keywords}')
            return self.save(dry)
        return False

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

    def fix(self, checks: Optional[Iterable[str]] = None, dry: Optional[bool] = None) -> bool:
        checks = checks if checks is not None else DEFAULT_CHECKS
        dry = dry if dry is not None else False
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
            if not dry:
                ensure(self.canonic_path)
                path = pathlib.Path(self.path)
                path.replace(self.canonic_path)
                self.path = self.canonic_path
                self.handle = mutagen.File(self.path)
                self.inconsistencies.remove('invalid-path')
        return self.save(dry)

    def save(self, dry: Optional[bool] = None) -> bool:
        dry = dry if dry is not None else False
        try:
            if not dry:
                self.handle.save()
            return True
        except mutagen.MutagenError as e:
            logger.error(e)
        return False
