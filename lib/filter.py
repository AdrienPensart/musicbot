# -*- coding: utf-8 -*-
from .lib import convert_rating
from bson.json_util import dumps
default_min_rating = 0.0
default_max_rating = 5.0
rating_choices = [str(x * 0.5) for x in range(0, 11)]
default_formats = ["mp3", "flac"]
min_int = 0
max_int = 2147483647
default_max_limit = max_int
default_min_size = min_int
default_max_size = max_int
default_min_duration = min_int
default_max_duration = max_int


class Filter(object):

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if value is not None:
                setattr(self, key, value)
        self.min_rating = convert_rating(float(self.min_rating))
        self.max_rating = convert_rating(float(self.max_rating))
        assert self.min_duration <= self.max_duration
        assert self.min_rating <= self.max_rating
        assert len(set(self.formats).intersection(self.no_formats)) == 0
        assert len(set(self.artists).intersection(self.no_artists)) == 0
        assert len(set(self.genres).intersection(self.no_genres)) == 0
        assert len(set(self.albums).intersection(self.no_albums)) == 0
        assert len(set(self.titles).intersection(self.no_titles)) == 0
        assert len(set(self.keywords).intersection(self.no_keywords)) == 0
        assert len(set(self.checks).intersection(self.no_checks)) == 0

    def __repr__(self):
        return dumps(self.to_list())

    def to_list(self):
        # return [a for a in dir(self) if not a.startswith('__')]
        my_list = [self.id,
                   self.min_duration, self.max_duration,
                   self.min_size, self.max_size,
                   self.min_rating, self.max_rating,
                   self.artists, self.no_artists,
                   self.albums, self.no_albums,
                   self.titles, self.no_titles,
                   self.genres, self.no_genres,
                   self.formats, self.no_formats,
                   self.keywords, self.no_keywords,
                   self.shuffle, self.relative, self.limit, self.youtube]
        return my_list

    @property
    def comment(self, defaults=''):
        return self.__get_first('COMMENT', defaults)

    id = 0
    relative = False
    shuffle = False
    youtube = None
    formats = default_formats
    no_formats = list()
    genres = list()
    no_genres = list()
    limit = default_max_limit
    min_duration = default_min_duration
    max_duration = default_max_duration
    min_size = default_min_size
    max_size = default_max_size
    min_rating = default_min_rating
    max_rating = default_max_rating
    keywords = list()
    no_keywords = list()
    artists = list()
    no_artists = list()
    titles = list()
    no_titles = list()
    albums = list()
    no_albums = list()
    checks = list()
    no_checks = list()
