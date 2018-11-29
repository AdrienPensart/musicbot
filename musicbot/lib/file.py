import taglib
import click
import copy
import os
from . import youtube


options = [
    click.option('--keywords', envvar='MB_KEYWORDS', help='Keywords', default=None),
    click.option('--artist', envvar='MB_ARTIST', help='Artist', default=None),
    click.option('--album', envvar='MB_ALBUM', help='Album', default=None),
    click.option('--title', envvar='MB_TITLE', help='Title', default=None),
    click.option('--genre', envvar='MB_GENRE', help='Genre', default=None),
    click.option('--number', envvar='MB_NUMBER', help='Track number', default=None),
    click.option('--rating', envvar='MB_RATING', help='Rating', default=None),
]


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

    def close(self):
        self.handle.close()

    def to_list(self):
        return [self.title,
                self.album,
                self.genre,
                self.artist,
                self._folder,
                self.youtube,
                self.spotify,
                self.number,
                self.path,
                self.rating,
                self.duration,
                self.size,
                mysplit(self.keywords, ' ')
                ]

    def to_tuple(self):
        return (self.title,
                self.album,
                self.genre,
                self.artist,
                self._folder,
                self.youtube,
                self.spotify,
                self.number,
                self.path,
                self.rating,
                self.duration,
                self.size,
                mysplit(self.keywords, ' '))

    @staticmethod
    def keys():
        return ['title', 'album', 'genre', 'artist', 'folder', 'youtube', 'spotify', 'number', 'path', 'rating', 'duration', 'size', 'keywords']

    # def to_dict(self):
    #     from collections import OrderedDict
    #     return OrderedDict([('title', self.title),
    #                         ('album', self.genre),
    #                         ('genre', self.genre),
    #                         ('artist', self.artist),
    #                         ('folder', self._folder),
    #                         ('youtube', self.youtube),
    #                         ('spotify', self.spotify),
    #                         ('number', self.number),
    #                         ('path', self.path),
    #                         ('rating', self.rating),
    #                         ('duration', self.duration),
    #                         ('size', self.size),
    #                         ('keywords', mysplit(self.keywords, ' '))])

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
    def title(self, default=''):
        return self.__get_first('TITLE', default)

    @title.setter
    def title(self, title):
        self.__set_first('TITLE', title)

    @property
    def album(self, default=''):
        return self.__get_first('ALBUM', default)

    @album.setter
    def album(self, album):
        self.__set_first('ALBUM', album)

    @property
    def artist(self, default=''):
        return self.__get_first('ARTIST', default)

    @artist.setter
    def artist(self, artist):
        self.__set_first('ARTIST', artist)

    @property
    def rating(self, default=0.0):
        s = self.__get_first('FMPS_RATING', default)
        try:
            n = float(s)
            if n < 0.0:
                return default
            return n * 5.0
        except ValueError:
            return default

    @rating.setter
    def rating(self, rating):
        self.__set_first('FMPS_RATING', rating)

    @property
    def comment(self, defaults=''):
        return self.__get_first('COMMENT', defaults)

    @comment.setter
    def comment(self, comment):
        self.__set_first('COMMENT', comment)

    def fix_comment(self, comment):
        self.__set_first('COMMENT', comment, force=True)

    @property
    def description(self, default=''):
        return self.__get_first('DESCRIPTION', default)

    @description.setter
    def description(self, description):
        self.__set_first('DESCRIPTION', description)

    def fix_description(self, description):
        self.__set_first('DESCRIPTION', description, force=True)

    @property
    def genre(self, default=''):
        return self.__get_first('GENRE', default)

    @genre.setter
    def genre(self, genre):
        self.__set_first('GENRE', genre)

    @property
    def number(self, default=-1):
        s = self.__get_first('TRACKNUMBER', default)
        try:
            n = int(s)
            if n < 0:
                return default
            return n
        except ValueError:
            return default

    @number.setter
    def number(self, number):
        self.__set_first('TRACKNUMBER', number)

    @property
    def keywords(self):
        if self.handle.path.endswith('.mp3'):
            return self.comment
        if self.handle.path.endswith('.flac'):
            if self.comment and not self.description:
                self.fix_description(self.comment)
            return self.description
        return ''

    @keywords.setter
    def keywords(self, keywords):
        if self.handle.path.endswith('.mp3'):
            self.comment = keywords
        elif self.handle.path.endswith('.flac'):
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

    async def find_youtube(self):
        self.youtube_link = await youtube.search(self.artist, self.title, self.duration)

    def save(self):
        self.handle.save()
