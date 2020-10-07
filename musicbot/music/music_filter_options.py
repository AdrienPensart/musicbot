from typing import Any
import click
import attr
from click_option_group import optgroup  # type: ignore
from musicbot import defaults
from musicbot.music.music_filter import MusicFilter


def sane_rating(ctx: click.Context, param: click.ParamType, value: float) -> float:
    if value in defaults.RATING_CHOICES:
        ctx.params[param.name] = value
        return value
    return float('nan')


def sane_music_filter(ctx: click.Context, param: click.ParamType, value: Any) -> MusicFilter:  # pylint: disable=unused-argument
    kwargs = {}
    for field in attr.fields_dict(MusicFilter):
        kwargs[field] = ctx.params[field]
        ctx.params.pop(field)

    myfilter = MusicFilter(**kwargs)
    ctx.params[param.name] = myfilter
    return myfilter


shuffle_option = optgroup.option(
    '--shuffle',
    help='Randomize selection',
    default=defaults.DEFAULT_SHUFFLE,
    is_flag=True,
    is_eager=True,
)
interleave_option = optgroup.option(
    '--interleave',
    help='Interleave tracks by artist',
    is_flag=True,
)
ordering_options = [
    optgroup.group('Ordering options'),
    shuffle_option,
    interleave_option,
]

options = [
    optgroup.group('Filter options'),
    optgroup.option(
        '--music-filter',
        help='Music Filter',
        expose_value=False,
        callback=sane_music_filter,
        hidden=True,
    ),
    optgroup.option(
        '--name',
        help='Filter name',
        default=defaults.DEFAULT_NAME,
        is_eager=True,
    ),
    optgroup.option(
        '--limit',
        help='Fetch a maximum limit of music',
        default=defaults.DEFAULT_LIMIT,
        is_eager=True,
    ),
    optgroup.option(
        '--youtubes',
        help='Select musics with a youtube link',
        multiple=True,
        default=defaults.DEFAULT_YOUTUBES,
        is_eager=True,
    ),
    optgroup.option(
        '--no-youtubes',
        help='Select musics without youtube link',
        multiple=True,
        default=defaults.DEFAULT_NO_YOUTUBES,
        is_eager=True,
    ),
    optgroup.option(
        '--spotifys',
        help='Select musics with a spotifys link',
        multiple=True,
        default=defaults.DEFAULT_YOUTUBES,
        is_eager=True,
    ),
    optgroup.option(
        '--no-spotifys',
        help='Select musics without spotifys link',
        multiple=True,
        default=defaults.DEFAULT_NO_YOUTUBES,
        is_eager=True,
    ),
    optgroup.option(
        '--formats',
        help='Select musics with file format',
        multiple=True,
        default=defaults.DEFAULT_FORMATS,
        is_eager=True,
    ),
    optgroup.option(
        '--no-formats',
        help='Filter musics without format',
        multiple=True,
        default=defaults.DEFAULT_NO_FORMATS,
        is_eager=True,
    ),
    optgroup.option(
        '--keywords',
        help='Select musics with keywords',
        multiple=True,
        default=defaults.DEFAULT_KEYWORDS,
        is_eager=True,
    ),
    optgroup.option(
        '--no-keywords',
        help='Filter musics without keywords',
        multiple=True,
        default=defaults.DEFAULT_NO_KEYWORDS,
        is_eager=True,
    ),
    optgroup.option(
        '--artists',
        help='Select musics with artists',
        multiple=True,
        default=defaults.DEFAULT_ARTISTS,
        is_eager=True,
    ),
    optgroup.option(
        '--no-artists',
        help='Filter musics without artists',
        multiple=True,
        default=defaults.DEFAULT_NO_ARTISTS,
        is_eager=True,
    ),
    optgroup.option(
        '--albums',
        help='Select musics with albums',
        multiple=True,
        default=defaults.DEFAULT_ALBUMS,
        is_eager=True,
    ),
    optgroup.option(
        '--no-albums',
        help='Filter musics without albums',
        multiple=True,
        default=defaults.DEFAULT_NO_ALBUMS,
        is_eager=True,
    ),
    optgroup.option(
        '--titles',
        help='Select musics with titles',
        multiple=True,
        default=defaults.DEFAULT_TITLES,
        is_eager=True,
    ),
    optgroup.option(
        '--no-titles',
        help='Filter musics without titless',
        multiple=True,
        default=defaults.DEFAULT_NO_TITLES,
        is_eager=True,
    ),
    optgroup.option(
        '--genres',
        help='Select musics with genres',
        multiple=True,
        default=defaults.DEFAULT_GENRES,
        is_eager=True,
    ),
    optgroup.option(
        '--no-genres',
        help='Filter musics without genres',
        multiple=True,
        default=defaults.DEFAULT_NO_GENRES,
        is_eager=True,
    ),
    optgroup.option(
        '--min-duration',
        help='Minimum duration filter (hours:minutes:seconds)',
        default=defaults.DEFAULT_MIN_DURATION,
        is_eager=True,
    ),
    optgroup.option(
        '--max-duration',
        help='Maximum duration filter (hours:minutes:seconds))',
        default=defaults.DEFAULT_MAX_DURATION,
        is_eager=True,
    ),
    optgroup.option(
        '--min-size',
        help='Minimum file size filter (in bytes)',
        default=defaults.DEFAULT_MIN_SIZE,
        is_eager=True,
    ),
    optgroup.option(
        '--max-size',
        help='Maximum file size filter (in bytes)',
        default=defaults.DEFAULT_MAX_SIZE,
        is_eager=True,
    ),
    optgroup.option(
        '--min-rating',
        help='Minimum rating',
        default=defaults.DEFAULT_MIN_RATING,
        show_default=True,
        callback=sane_rating,
        is_eager=True,
    ),
    optgroup.option(
        '--max-rating',
        help='Maximum rating',
        default=defaults.DEFAULT_MAX_RATING,
        show_default=True,
        callback=sane_rating,
        is_eager=True,
    ),
    optgroup.option(
        '--relative',
        help='Generate relatives paths',
        default=defaults.DEFAULT_RELATIVE,
        is_flag=True,
        is_eager=True,
    ),
    optgroup.option(
        '--shuffle',
        help='Randomize selection',
        default=defaults.DEFAULT_SHUFFLE,
        is_flag=True,
        is_eager=True,
    ),
    optgroup.group('Ordering options'),
    shuffle_option,
]
