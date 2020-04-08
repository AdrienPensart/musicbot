import logging
import json
import copy
import os
import click
import taglib


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
        self._folder = _folder
        self.handle = taglib.File(filename)
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
        return self.handle.path

    @property
    def folder(self):
        return self._folder

    def __get_first(self, tag, default=''):
        if tag not in self.handle.tags:
            return default
        for item in self.handle.tags[tag]:
            return str(item)
        return default

    def __set_first(self, tag, value, force=False):
        if value is None:
            return
        if tag not in self.handle.tags:
            if force:
                self.handle.tags[tag] = [value]
            return
        del self.handle.tags[tag][0]
        self.handle.tags[tag].insert(0, value)

    @property
    def title(self):
        return self.__get_first('TITLE')

    @title.setter
    def title(self, title):
        self.__set_first('TITLE', title)

    @property
    def album(self):
        return self.__get_first('ALBUM')

    @album.setter
    def album(self, album):
        self.__set_first('ALBUM', album)

    @property
    def artist(self):
        return self.__get_first('ARTIST')

    @artist.setter
    def artist(self, artist):
        self.__set_first('ARTIST', artist)

    @property
    def rating(self):
        s = self.__get_first('FMPS_RATING')
        try:
            n = float(s)
            if n < 0.0:
                return 0.0
            return n * 5.0
        except ValueError:
            return 0.0

    @rating.setter
    def rating(self, rating):
        self.__set_first('FMPS_RATING', rating)

    @property
    def comment(self):
        return self.__get_first('COMMENT')

    @comment.setter
    def comment(self, comment):
        self.__set_first('COMMENT', comment)

    def fix_comment(self, comment):
        self.__set_first('COMMENT', comment, force=True)

    @property
    def description(self):
        return self.__get_first('DESCRIPTION')

    @description.setter
    def description(self, description):
        self.__set_first('DESCRIPTION', description)

    def fix_description(self, description):
        self.__set_first('DESCRIPTION', description, force=True)

    @property
    def genre(self):
        return self.__get_first('GENRE')

    @genre.setter
    def genre(self, genre):
        self.__set_first('GENRE', genre)

    @property
    def number(self):
        s = self.__get_first('TRACKNUMBER')
        try:
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
        self.__set_first('TRACKNUMBER', number)

    @property
    def keywords(self):
        if str(self.handle.path).endswith('.mp3'):
            return self.comment
        if str(self.handle.path).endswith('.flac'):
            if self.comment and not self.description:
                self.fix_description(self.comment)
            return self.description
        return ''

    @keywords.setter
    def keywords(self, keywords):
        if str(self.handle.path).endswith('.mp3'):
            self.comment = keywords
        elif str(self.handle.path).endswith('.flac'):
            self.fix_description(keywords)

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
    def duration(self):
        return self.handle.length

    @property
    def size(self):
        return os.path.getsize(self.handle.path)

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
            logger.info("score : %s | recording_id : %s | title : %s | artist : %s", score, recording_id, title, artist)
            return recording_id
        return None

    def save(self):
        self.handle.save()
