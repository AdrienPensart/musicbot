import logging
import json
from typing import Any, Dict, List, Optional
import attr
import click
from click_option_group import optgroup  # type: ignore

logger = logging.getLogger(__name__)


rating_choices = [x * 0.5 for x in range(0, 11)]


def sane_rating(ctx: click.Context, param: click.ParamType, value: float) -> float:
    if value is not None and value in rating_choices:
        ctx.params[param.name] = value
        return value
    return float('nan')


min_int = 0
max_int = 2147483647

default_name: Optional[str] = None
default_filter = None
default_relative = False
default_shuffle = False
default_youtubes: List[str] = []
default_no_youtubes: List[str] = []
default_spotifys: List[str] = []
default_no_spotifys: List[str] = []
default_formats: List[str] = []
default_no_formats: List[str] = []
default_genres: List[str] = []
default_no_genres: List[str] = []
default_limit: int = max_int
default_min_duration: int = min_int
default_max_duration: int = max_int
default_min_size: int = min_int
default_max_size: int = max_int
default_min_rating = min(rating_choices)
default_max_rating = max(rating_choices)
default_keywords: List[str] = []
default_no_keywords: List[str] = []
default_artists: List[str] = []
default_no_artists: List[str] = []
default_titles: List[str] = []
default_no_titles: List[str] = []
default_albums: List[str] = []
default_no_albums: List[str] = []


@attr.s(auto_attribs=True, frozen=True)
class Filter:
    name: Optional[str] = default_name
    relative: bool = default_relative
    shuffle: bool = default_shuffle
    min_duration: int = default_min_duration
    max_duration: int = default_max_duration
    min_size: int = default_min_size
    max_size: int = default_max_size
    min_rating: float = default_min_rating
    max_rating: float = default_max_rating
    youtubes: List[str] = default_youtubes
    no_youtubes: List[str] = default_no_youtubes
    spotifys: List[str] = default_spotifys
    no_spotifys: List[str] = default_no_spotifys
    formats: List[str] = default_formats
    no_formats: List[str] = default_no_formats
    limit: int = default_limit
    genres: List[str] = default_genres
    no_genres: List[str] = default_no_genres
    keywords: List[str] = default_keywords
    no_keywords: List[str] = default_no_keywords
    artists: List[str] = default_artists
    no_artists: List[str] = default_no_artists
    titles: List[str] = default_titles
    no_titles: List[str] = default_no_titles
    albums: List[str] = default_albums
    no_albums: List[str] = default_no_albums

    def __attrs_post_init__(self) -> None:
        if self.min_size > self.max_size:
            raise ValueError(f"Invalid minimum ({self.min_rating}) or maximum ({self.max_rating}) size")

        if self.min_rating not in rating_choices:
            raise ValueError(f"Invalid minimum rating {self.min_rating}, it should be one of {rating_choices}")

        if self.max_rating not in rating_choices:
            raise ValueError(f"Invalid maximum rating {self.max_rating}, it should be one of {rating_choices}")

        if self.min_rating > self.max_rating:
            raise ValueError(f"Invalid minimum ({self.min_rating}) or maximum ({self.max_rating}) rating")

        if self.min_duration > self.max_duration:
            raise ValueError(f"Invalid minimum ({self.min_duration}) or maximum ({self.max_duration}) duration")

        is_bad_formats = set(self.formats).intersection(self.no_formats)
        is_bad_artists = set(self.artists).intersection(self.no_artists)
        is_bad_genres = set(self.genres).intersection(self.no_genres)
        is_bad_albums = set(self.albums).intersection(self.no_albums)
        is_bad_titles = set(self.titles).intersection(self.no_titles)
        is_bad_keywords = set(self.keywords).intersection(self.no_keywords)
        not_empty_set = is_bad_formats or is_bad_artists or is_bad_genres or is_bad_albums or is_bad_titles or is_bad_keywords
        if not_empty_set:
            raise ValueError(f"You can't have duplicates value in filters {self}")
        logger.debug(f'Filter: {self}')

    def __repr__(self) -> str:
        return json.dumps(self.as_dict())

    def diff(self) -> Dict[str, Any]:
        '''Print only differences with default filter'''
        myself = vars(self)
        default = vars(Filter())
        return {k: myself[k] for k in myself if default[k] != myself[k] and k != 'name'}

    def common(self) -> Dict[str, Any]:
        '''Print common values with default filter'''
        myself = vars(self)
        default = vars(Filter())
        return {k: myself[k] for k in myself if default[k] == myself[k] and k != 'name'}

    def as_dict(self) -> Dict[str, Any]:  # pylint: disable=unsubscriptable-object
        return {
            'minDuration': self.min_duration,
            'maxDuration': self.max_duration,
            'minSize': self.min_size,
            'maxSize': self.max_size,
            'minRating': self.min_rating,
            'maxRating': self.max_rating,
            'artists': self.artists,
            'noArtists': self.no_artists,
            'albums': self.albums,
            'noAlbums': self.no_albums,
            'titles': self.titles,
            'noTitles': self.no_titles,
            'genres': self.genres,
            'noGenres': self.no_genres,
            'formats': self.formats,
            'noFormats': self.no_formats,
            'keywords': self.keywords,
            'noKeywords': self.no_keywords,
            'shuffle': self.shuffle,
            'relative': self.relative,
            'limit': self.limit,
            'youtubes': self.youtubes,
            'noYoutubes': self.no_youtubes,
            'spotifys': self.spotifys,
            'noSpotifys': self.no_spotifys,
        }

    def to_graphql(self) -> str:
        return ", ".join([f'{k}: {json.dumps(v)}' for k, v in self.as_dict().items()])


options = [
    optgroup.option(
        '--name',
        help='Filter name',
        default=default_name,
        is_eager=True,
    ),
    optgroup.option(
        '--limit',
        help='Fetch a maximum limit of music',
        default=default_limit,
        is_eager=True,
    ),
    optgroup.option(
        '--youtubes',
        help='Select musics with a youtube link',
        multiple=True,
        default=default_youtubes,
        is_eager=True,
    ),
    optgroup.option(
        '--no-youtubes',
        help='Select musics without youtube link',
        multiple=True,
        default=default_no_youtubes,
        is_eager=True,
    ),
    optgroup.option(
        '--spotifys',
        help='Select musics with a spotifys link',
        multiple=True,
        default=default_youtubes,
        is_eager=True,
    ),
    optgroup.option(
        '--no-spotifys',
        help='Select musics without spotifys link',
        multiple=True,
        default=default_no_youtubes,
        is_eager=True,
    ),
    optgroup.option(
        '--formats',
        help='Select musics with file format',
        multiple=True,
        default=default_formats,
        is_eager=True,
    ),
    optgroup.option(
        '--no-formats',
        help='Filter musics without format',
        multiple=True,
        default=default_no_formats,
        is_eager=True,
    ),
    optgroup.option(
        '--keywords',
        help='Select musics with keywords',
        multiple=True,
        default=default_keywords,
        is_eager=True,
    ),
    optgroup.option(
        '--no-keywords',
        help='Filter musics without keywords',
        multiple=True,
        default=default_no_keywords,
        is_eager=True,
    ),
    optgroup.option(
        '--artists',
        help='Select musics with artists',
        multiple=True,
        default=default_artists,
        is_eager=True,
    ),
    optgroup.option(
        '--no-artists',
        help='Filter musics without artists',
        multiple=True,
        default=default_no_artists,
        is_eager=True,
    ),
    optgroup.option(
        '--albums',
        help='Select musics with albums',
        multiple=True,
        default=default_albums,
        is_eager=True,
    ),
    optgroup.option(
        '--no-albums',
        help='Filter musics without albums',
        multiple=True,
        default=default_no_albums,
        is_eager=True,
    ),
    optgroup.option(
        '--titles',
        help='Select musics with titles',
        multiple=True,
        default=default_titles,
        is_eager=True,
    ),
    optgroup.option(
        '--no-titles',
        help='Filter musics without titless',
        multiple=True,
        default=default_no_titles,
        is_eager=True,
    ),
    optgroup.option(
        '--genres',
        help='Select musics with genres',
        multiple=True,
        default=default_genres,
        is_eager=True,
    ),
    optgroup.option(
        '--no-genres',
        help='Filter musics without genres',
        multiple=True,
        default=default_no_genres,
        is_eager=True,
    ),
    optgroup.option(
        '--min-duration',
        help='Minimum duration filter (hours:minutes:seconds)',
        default=default_min_duration,
        is_eager=True,
    ),
    optgroup.option(
        '--max-duration',
        help='Maximum duration filter (hours:minutes:seconds))',
        default=default_max_duration,
        is_eager=True,
    ),
    optgroup.option(
        '--min-size',
        help='Minimum file size filter (in bytes)',
        default=default_min_size,
        is_eager=True,
    ),
    optgroup.option(
        '--max-size',
        help='Maximum file size filter (in bytes)',
        default=default_max_size,
        is_eager=True,
    ),
    optgroup.option(
        '--min-rating',
        help='Minimum rating',
        default=default_min_rating,
        show_default=True,
        callback=sane_rating,
        is_eager=True,
    ),
    optgroup.option(
        '--max-rating',
        help='Maximum rating',
        default=default_max_rating,
        show_default=True,
        callback=sane_rating,
        is_eager=True,
    ),
    optgroup.option(
        '--relative',
        help='Generate relatives paths',
        default=default_relative,
        is_flag=True,
        is_eager=True,
    ),
    optgroup.option(
        '--shuffle',
        help='Randomize selection',
        default=default_shuffle,
        is_flag=True,
        is_eager=True,
    ),
]


def sane_filter(ctx: click.Context, param: click.ParamType, value: Any) -> Filter:  # pylint: disable=unused-argument
    kwargs = {}
    for field in attr.fields_dict(Filter):
        kwargs[field] = ctx.params[field]
        ctx.params.pop(field)

    myfilter = Filter(**kwargs)
    ctx.params['music_filter'] = myfilter
    return myfilter


DEFAULT_FILTER = None
mfilter_option = [
    optgroup.option(
        '--music-filter',
        help='Music Filter',
        expose_value=False,
        callback=sane_filter,
        hidden=True,
    )
]
mfilter_options =\
    [optgroup.group('Filter options')] +\
    mfilter_option +\
    options
