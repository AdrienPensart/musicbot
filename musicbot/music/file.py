import logging
import json
import copy
import os
import click
import mutagen
from mutagen.id3 import TXXX, TRCK, TIT2, TALB, TPE1, TCON, COMM


logger = logging.getLogger(__name__)
options = [
    click.option('--keywords', help='Keywords', default=None),
    click.option('--artist', help='Artist', default=None),
    click.option('--album', help='Album', default=None),
    click.option('--title', help='Title', default=None),
    click.option('--genre', help='Genre', default=None),
    click.option('--number', help='Track number', default=None),
    click.option('--rating', help='Rating', default=None),
]
checks = ['no-title', 'no-artist', 'no-album', 'no-genre', 'no-rating', 'no-tracknumber', 'invalid-title', 'invalid-artist', 'invalid-comment']
checks_options = [
    click.option(
        '--checks',
        help='Consistency tests',
        multiple=True,
        default=checks,
        show_default=True,
        type=click.Choice(checks)
    ),
    click.option('--fix', is_flag=True),
]
supported_formats = ["mp3", "flac"]


def mysplit(s, delim=','):
    if isinstance(s, list):
        return s
    if s is None:
        return []
    if isinstance(s, str):
        return [x for x in s.split(delim) if x]
    raise ValueError(s)


# pylint: disable-msg=unsupported-membership-test
# pylint: disable-msg=unsubscriptable-object
# pylint: disable-msg=unsupported-assignment-operation
class File:
    def __init__(self, filename, _folder=''):
        self.handle = mutagen.File(filename)
        self._folder = _folder
        self.filename = filename
        self.youtube_link = ''
        self.spotify_link = ''

    def __repr__(self):
        return self.path

    def close(self):
        self.handle.close()

    def ordered_dict(self):
        from collections import OrderedDict
        return OrderedDict([('title', self.title),
                            ('album', self.album),
                            ('genre', self.genre),
                            ('artist', self.artist),
                            ('folder', self._folder),
                            ('youtube', self.youtube),
                            ('spotify', self.spotify),
                            ('number', self.number),
                            ('path', self.path),
                            ('rating', self.rating),
                            ('duration', self.duration),
                            ('size', self.size),
                            ('keywords', mysplit(self.keywords, ' '))])

    def __iter__(self):
        yield from self.ordered_dict().items()

    def to_dict(self):
        return dict(self.ordered_dict())

    def to_graphql(self):
        return ", ".join([f'{k}: {json.dumps(v)}' for k, v in self.ordered_dict().items()])

    def to_json(self):
        return json.dumps(self.ordered_dict())

    @property
    def path(self):
        return self.filename

    @property
    def folder(self):
        return self._folder

    def _get_first(self, tag, default=''):
        if tag not in self.handle:
            return default
        for item in self.handle[tag]:
            return str(item)
        return default

    @property
    def duration(self):
        return int(self.handle.info.length)

    @property
    def size(self):
        return os.path.getsize(self.filename)

    @property
    def title(self):
        if self.filename.endswith('flac'):
            return self._get_first('title')
        return self._get_first('TIT2')

    @title.setter
    def title(self, title):
        if self.filename.endswith('flac'):
            self.handle.tags['title'] = title
        else:
            self.handle.tags.add(TIT2(text=title))

    @property
    def album(self):
        if self.filename.endswith('flac'):
            return self._get_first('album')
        return self._get_first('TALB')

    @album.setter
    def album(self, album):
        if self.filename.endswith('flac'):
            self.handle.tags['album'] = album
        else:
            self.handle.tags.add(TALB(text=album))

    @property
    def artist(self):
        if self.filename.endswith('flac'):
            return self._get_first('artist')
        return self._get_first('TPE1')

    @artist.setter
    def artist(self, artist):
        if self.filename.endswith('flac'):
            self.handle.tags['artist'] = artist
        else:
            self.handle.tags.add(TPE1(text=artist))

    @property
    def genre(self):
        if self.filename.endswith('flac'):
            return self._get_first('genre')
        return self._get_first('TCON')

    @genre.setter
    def genre(self, genre):
        if self.filename.endswith('flac'):
            self.handle.tags['genre'] = genre
        else:
            self.handle.tags.add(TCON(text=genre))

    @property
    def rating(self):
        if self.filename.endswith('flac'):
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
    def rating(self, rating):
        if self.filename.endswith('flac'):
            self.handle['fmps_rating'] = str(rating)
        else:
            self.handle.tags.add(TXXX(desc='FMPS_Rating', text=str(rating)))

    @property
    def _comment(self):
        return self._get_first('COMM:ID3v1 Comment:eng')

    @_comment.setter
    def _comment(self, comment):
        self.handle.tags.add(COMM(desc='ID3v1 Comment:eng', text=str(comment)))

    @property
    def _description(self):
        return self._get_first('description')

    @_description.setter
    def _description(self, description):
        self.handle.tags['description'] = description

    @property
    def number(self):
        if self.filename.endswith('flac'):
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
                logger.warning("%s : invalid number %s", self, n)
                return 0
            return n
        except ValueError:
            return -1

    @number.setter
    def number(self, number):
        if self.filename.endswith('flac'):
            self.handle.tags['tracknumber'] = str(number)
        else:
            self.handle.tags.add(TRCK(text=str(number)))

    @property
    def keywords(self):
        if str(self.filename).endswith('mp3'):
            return self._comment
        if str(self.filename).endswith('flac'):
            if self._comment and not self._description:
                self.description = self._comment
            return self._description
        return ''

    @keywords.setter
    def keywords(self, keywords):
        if str(self.filename).endswith('mp3'):
            self._comment = keywords
        elif str(self.filename).endswith('flac'):
            self.description = keywords

    def add_keywords(self, keywords):
        tags = copy.deepcopy(self.keywords)
        for k in keywords:
            if k not in tags:
                tags.append(k)
        if set(self.keywords) != set(tags):
            self.keywords = tags
            self.save()
            return True
        return False

    def delete_keywords(self, keywords):
        tags = copy.deepcopy(self.keywords)
        for k in keywords:
            if k in tags:
                tags.remove(k)
        if set(self.keywords) != set(tags):
            self.keywords = tags
            self.save()
            return True
        return False

    @property
    def youtube(self):
        return self.youtube_link

    @property
    def spotify(self):
        return self.spotify_link

    def fingerprint(self, api_key):
        import acoustid
        ids = acoustid.match(api_key, self.path)
        for score, recording_id, title, artist in ids:
            logger.info(f"score : {score} | recording_id : {recording_id} | title : {title} | artist : {artist}")
            return recording_id
        return None

    def check_consistency(self, checks, fix):
        inconsistencies = []
        if 'no-title' in checks:
            if not self.title:
                inconsistencies.append("no-title")
        if 'no-genre' in checks:
            if self.genre == '':
                inconsistencies.append("no-genre")
        if 'no-album' in checks:
            if self.album == '':
                inconsistencies.append("no-album")
        if 'no-artist' in checks:
            if self.artist == '':
                inconsistencies.append("no-artist")
        if 'invalid-comment' in checks:
            if self.filename.endswith('flac'):
                if self._comment and not self._description:
                    inconsistencies.append(f'invalid-comment comment {self._comment} used in flac instead of description')
                    if fix:
                        self._description = ''
            if self.path.endswith('mp3'):
                if self._description and not self._comment:
                    inconsistencies.append(f'invalid-comment description {self._description} used in mp3 instead of comment')
                    if fix:
                        self._comment = ''
        if 'invalid-artist' in checks:
            if self.artist not in self.path:
                inconsistencies.append(f"invalid-artist : {self.artist} is not in path")
        if 'no-rating' in checks:
            if self.rating == -1:
                inconsistencies.append("no-rating")
                if fix:
                    self.rating = 0.0
        if self.number == -1:
            if 'no-tracknumber' in checks:
                inconsistencies.append("no-tracknumber")
                if fix:
                    self.number = 0
        if self.number not in (-1, 0) and 'invalid-title' in checks:
            filename = os.path.basename(self.path)
            if filename != f"{str(self.number).zfill(2)} - {self.title}.mp3" or filename != f"{str(self.number).zfill(2)} - {self.title}.flac":
                inconsistencies.append(f"invalid-title, '{self.filename}' should start by '{str(self.number).zfill(2)} - {self.title}'")
        if inconsistencies and fix:
            self.save()
        return inconsistencies

    def save(self):
        self.handle.save()
