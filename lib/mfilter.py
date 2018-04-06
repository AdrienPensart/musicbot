# -*- coding: utf-8 -*-
from logging import debug
import click
import json

rating_choices = [x * 0.5 for x in range(0, 11)]
min_int = 0
max_int = 2147483647

default_name = ''
default_filter = None
default_relative = False
default_shuffle = False
default_youtube = None
supported_formats = ["mp3", "flac"]
default_formats = []
default_no_formats = []
default_genres = []
default_no_genres = []
default_limit = max_int
default_min_duration = min_int
default_max_duration = max_int
default_min_size = min_int
default_max_size = max_int
default_min_rating = 0.0
default_max_rating = 5.0
default_keywords = []
default_no_keywords = []
default_artists = []
default_no_artists = []
default_titles = []
default_no_titles = []
default_albums = []
default_no_albums = []


class Filter(object):

    def __init__(self, name=None, relative=None, shuffle=None, youtube=None, formats=None, no_formats=None, genres=None, no_genres=None, limit=None, min_duration=None, max_duration=None, min_size=None, max_size=None, min_rating=None, max_rating=None, keywords=None, no_keywords=None, artists=None, no_artists=None, titles=None, no_titles=None, albums=None, no_albums=None, **kwargs):
        self.id = 0
        self.name = default_name if name is None else name
        self.relative = default_relative if relative is None else relative
        self.shuffle = default_shuffle if shuffle is None else shuffle
        self.youtube = default_youtube if youtube is None else youtube
        self.formats = default_formats if formats is None else formats
        self.no_formats = default_no_formats if no_formats is None else no_formats
        self.genres = default_genres if genres is None else genres
        self.no_genres = default_no_genres if no_genres is None else no_genres
        self.limit = default_limit if limit is None else limit
        self.min_duration = default_min_duration if min_duration is None else min_duration
        self.max_duration = default_max_duration if max_duration is None else max_duration
        self.min_size = default_min_size if min_size is None else min_size
        self.max_size = default_max_size if max_size is None else max_size
        self.min_rating = default_min_rating if min_rating is None else min_rating
        self.max_rating = default_max_rating if max_rating is None else max_rating
        self.keywords = default_keywords if keywords is None else keywords
        self.no_keywords = default_no_keywords if no_keywords is None else no_keywords
        self.artists = default_artists if artists is None else artists
        self.no_artists = default_no_artists if no_artists is None else no_artists
        self.titles = default_titles if titles is None else titles
        self.no_titles = default_no_titles if no_titles is None else no_titles
        self.albums = default_albums if albums is None else albums
        self.no_albums = default_no_albums if no_albums is None else no_albums
        debug('Filter: {}'.format(self))
        assert self.min_rating in rating_choices
        assert self.max_rating in rating_choices
        assert self.min_duration <= self.max_duration
        assert self.min_rating <= self.max_rating
        assert len(set(self.formats).intersection(self.no_formats)) == 0
        assert len(set(self.artists).intersection(self.no_artists)) == 0
        assert len(set(self.genres).intersection(self.no_genres)) == 0
        assert len(set(self.albums).intersection(self.no_albums)) == 0
        assert len(set(self.titles).intersection(self.no_titles)) == 0
        assert len(set(self.keywords).intersection(self.no_keywords)) == 0

    def __repr__(self):
        return json.dumps(self.to_list())

    def diff(self):
        '''Print only differences with default filter'''
        myself = vars(self)
        default = vars(Filter())
        return {k: myself[k] for k in myself if default[k] != myself[k] and k != 'name'}

    def common(self):
        '''Print common values with default filter'''
        myself = vars(self)
        default = vars(Filter())
        return {k: myself[k] for k in myself if default[k] == myself[k] and k != 'name'}

    def to_list(self):
        my_list = [self.id, self.name,
                   self.min_duration, self.max_duration,
                   self.min_size, self.max_size,
                   self.min_rating, self.max_rating,
                   self.artists, self.no_artists,
                   self.albums, self.no_albums,
                   self.titles, self.no_titles,
                   self.genres, self.no_genres,
                   self.formats, self.no_formats,
                   self.keywords, self.no_keywords,
                   self.shuffle, self.relative,
                   self.limit, self.youtube]
        return my_list


options = [
    click.option('--limit', envvar='MB_LIMIT', help='Fetch a maximum limit of music', default=default_limit),
    click.option('--youtube', envvar='MB_YOUTUBE', help='Select musics with a youtube link', default=default_youtube),
    click.option('--formats', envvar='MB_FORMATS', help='Select musics with file format', multiple=True, default=default_formats),
    click.option('--no-formats', envvar='MB_NO_FORMATS', help='Filter musics without format', multiple=True, default=default_no_formats),
    click.option('--keywords', envvar='MB_KEYWORDS', help='Select musics with keywords', multiple=True, default=default_keywords),
    click.option('--no-keywords', envvar='MB_NO_KEYWORDS', help='Filter musics without keywords', multiple=True, default=default_no_keywords),
    click.option('--artists', envvar='MB_ARTISTS', help='Select musics with artists', multiple=True, default=default_artists),
    click.option('--no-artists', envvar='MB_NO_ARTISTS', help='Filter musics without artists', multiple=True, default=default_no_artists),
    click.option('--albums', envvar='MB_ALBUMS', help='Select musics with albums', multiple=True, default=default_albums),
    click.option('--no-albums', envvar='MB_NO_ALBUMS', help='Filter musics without albums', multiple=True, default=default_no_albums),
    click.option('--titles', envvar='MB_TITLES', help='Select musics with titles', multiple=True, default=default_titles),
    click.option('--no-titles', envvar='MB_NO_TITLES', help='Filter musics without titless', multiple=True, default=default_no_titles),
    click.option('--genres', envvar='MB_GENRES', help='Select musics with genres', multiple=True, default=default_genres),
    click.option('--no-genres', envvar='MB_NO_GENRES', help='Filter musics without genres', multiple=True, default=default_no_genres),
    click.option('--min-duration', envvar='MB_MIN_DURATION', help='Minimum duration filter (hours:minutes:seconds)', default=default_min_duration),
    click.option('--max-duration', envvar='MB_MAX_DURATION', help='Maximum duration filter (hours:minutes:seconds))', default=default_max_duration),
    click.option('--min-size', envvar='MB_MIN_SIZE', help='Minimum file size filter (in bytes)', default=default_min_size),
    click.option('--max-size', envvar='MB_MAX_SIZE', help='Maximum file size filter (in bytes)', default=default_max_size),
    click.option('--min-rating', envvar='MB_MIN_RATING', help='Minimum rating', default=default_min_rating, show_default=True),
    click.option('--max-rating', envvar='MB_MAX_RATING', help='Maximum rating', default=default_max_rating, show_default=True),
    click.option('--relative', envvar='MB_RELATIVE', help='Generate relatives paths', default=default_relative, is_flag=True),
    click.option('--shuffle', envvar='MB_SHUFFLE', help='Randomize selection', default=default_shuffle, is_flag=True),
]
