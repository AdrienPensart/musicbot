# -*- coding: utf-8 -*-
import yaml
import json
from logging import debug


class Filter(object):

    def __init__(self, filter=None, **kwargs):
        if filter is not None:
            debug('Loading filter: {}'.format(self))
            self = yaml.load(filter)
        for key, value in kwargs.items():
            if hasattr(self, key) and value is not None:
                if value != getattr(Filter, key):
                    setattr(self, key, value)
        debug('Final: {}'.format(self))
        assert self.min_rating in self.rating_choices
        assert self.max_rating in self.rating_choices
        assert self.min_duration <= self.max_duration
        assert self.min_rating <= self.max_rating
        assert len(set(self.formats).intersection(self.no_formats)) == 0
        assert len(set(self.artists).intersection(self.no_artists)) == 0
        assert len(set(self.genres).intersection(self.no_genres)) == 0
        assert len(set(self.albums).intersection(self.no_albums)) == 0
        assert len(set(self.titles).intersection(self.no_titles)) == 0
        assert len(set(self.keywords).intersection(self.no_keywords)) == 0
        # assert len(set(self.checks).intersection(self.no_checks)) == 0

    def __repr__(self):
        return json.dumps(self.to_list())

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
    filter = None
    rating_choices = [x * 0.5 for x in range(0, 11)]
    min_int = 0
    max_int = 2147483647

    relative = False
    shuffle = False
    youtube = None
    formats = ("mp3", "flac")
    no_formats = tuple()
    genres = tuple()
    no_genres = tuple()
    limit = max_int
    min_duration = min_int
    max_duration = max_int
    min_size = min_int
    max_size = max_int
    min_rating = 0.0
    max_rating = 5.0
    keywords = tuple()
    no_keywords = tuple()
    artists = tuple()
    no_artists = tuple()
    titles = tuple()
    no_titles = tuple()
    albums = tuple()
    no_albums = tuple()
    # checks = list()
    # no_checks = list()
