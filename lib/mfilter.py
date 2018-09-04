import attr
import click
import logging
import json

logger = logging.getLogger(__name__)

rating_choices = [x * 0.5 for x in range(0, 11)]
min_int = 0
max_int = 2147483647

default_id = 0
default_name = ''
default_filter = None
default_relative = False
default_shuffle = False
default_youtubes = []
default_no_youtubes = []
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


@attr.s(frozen=True)
class Filter:
    id = attr.ib(default=default_id)
    name = attr.ib(default=default_name)
    relative = attr.ib(default=default_relative)
    shuffle = attr.ib(default=default_shuffle)
    youtubes = attr.ib(default=default_youtubes)
    no_youtubes = attr.ib(default=default_no_youtubes)
    formats = attr.ib(default=default_formats)
    no_formats = attr.ib(default=default_no_formats)
    limit = attr.ib(default=default_limit)
    genres = attr.ib(default=default_genres)
    no_genres = attr.ib(default=default_no_genres)
    genres = attr.ib(default=default_genres)
    no_genres = attr.ib(default=default_no_genres)
    min_duration = attr.ib(default=default_min_duration)
    max_duration = attr.ib(default=default_max_duration)
    min_size = attr.ib(default=default_min_size)
    max_size = attr.ib(default=default_max_size)
    min_rating = attr.ib(default=default_min_rating, validator=attr.validators.in_(rating_choices))
    max_rating = attr.ib(default=default_max_rating, validator=attr.validators.in_(rating_choices))
    keywords = attr.ib(default=default_keywords)
    no_keywords = attr.ib(default=default_no_keywords)
    artists = attr.ib(default=default_artists)
    no_artists = attr.ib(default=default_no_artists)
    titles = attr.ib(default=default_titles)
    no_titles = attr.ib(default=default_no_titles)
    albums = attr.ib(default=default_albums)
    no_albums = attr.ib(default=default_no_albums)

    def __attrs_post_init__(self):
        if self.min_rating > self.max_rating:
            raise ValueError("Invalid minimum ({}) or maximum ({}) rating".format(self.min_rating, self.max_rating))

        if self.min_duration > self.max_duration:
            raise ValueError("Invalid minimum ({}) or maximum ({}) duration".format(self.min_duration, self.max_duration))

        is_bad_formats = set(self.formats).intersection(self.no_formats)
        is_bad_artists = set(self.artists).intersection(self.no_artists)
        is_bad_genres = set(self.genres).intersection(self.no_genres)
        is_bad_albums = set(self.albums).intersection(self.no_albums)
        is_bad_titles = set(self.titles).intersection(self.no_titles)
        is_bad_keywords = set(self.keywords).intersection(self.no_keywords)
        not_empty_set = is_bad_formats or is_bad_artists or is_bad_genres or is_bad_albums or is_bad_titles or is_bad_keywords
        if not_empty_set:
            raise ValueError("You can't have duplicates value in filters {}".format(self))

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
                   self.limit, self.youtubes, self.no_youtubes]
        return my_list


options = [
    click.option('--limit', envvar='MB_LIMIT', help='Fetch a maximum limit of music', default=default_limit),
    click.option('--youtubes', envvar='MB_YOUTUBES', help='Select musics with a youtube link', default=default_youtubes),
    click.option('--no-youtubes', envvar='MB_NO_YOUTUBES', help='Select musics without youtube link', default=default_no_youtubes),
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
