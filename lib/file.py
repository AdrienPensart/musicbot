import taglib
import copy
import os
from . import youtube


def mysplit(s, delim=','):
    if type(s) is list:
        return s
    if s is None:
        return []
    if type(s) is str:
        return [x for x in s.split(delim) if x]
    raise ValueError(s)


class File(object):
    id = 0

    def __init__(self, filename, _folder=''):
        self._folder = _folder
        self.handle = taglib.File(filename)
        self.youtube_link = None

    def to_list(self):
        return [self.id,
                self.title,
                self.album,
                self.genre,
                self.artist,
                self._folder,
                self.youtube,
                self.number,
                self.path,
                self.rating,
                self.duration,
                self.size,
                self.keywords,
                ]

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
        if tag not in self.handle.tags:
            if force:
                self.handle.tags[tag] = [value]
            return
        del self.handle.tags[tag][0]
        self.handle.tags[tag].insert(0, value)

    @property
    def title(self, default=''):
        return self.__get_first('TITLE', default)

    @property
    def album(self, default=''):
        return self.__get_first('ALBUM', default)

    @property
    def artist(self, default=''):
        return self.__get_first('ARTIST', default)

    @property
    def rating(self, default=0.0):
        s = self.__get_first('FMPS_RATING', default)
        try:
            n = float(s)
            if n < 0.0:
                return default
            return n
        except ValueError:
            return default

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

    @property
    def keywords(self):
        if self.handle.path.endswith('.mp3'):
            return mysplit(self.comment, ' ')
        elif self.handle.path.endswith('.flac'):
            return mysplit(self.description, ' ')
        return mysplit(self.description, ' ') + mysplit(self.comment, ' ')

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

    @keywords.setter
    def keywords(self, keywords):
        if self.handle.path.endswith('.mp3'):
            self.comment = ' '.join(keywords)
        elif self.handle.path.endswith('.flac'):
            self.description = ' '.join(keywords)

    @property
    def duration(self):
        return self.handle.length

    @property
    def size(self):
        return os.path.getsize(self.handle.path)

    @property
    def youtube(self):
        return self.youtube_link

    def find_youtube(self):
        self.youtube_link = youtube.search(self)

    def save(self):
        self.handle.save()
