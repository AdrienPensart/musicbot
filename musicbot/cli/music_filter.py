from typing import Any

import attr
import click
from click_option_group import optgroup  # type: ignore
from click_skeleton import add_options
from click_skeleton.helpers import split_arguments

from musicbot.cli.options import sane_rating
from musicbot.defaults import (
    DEFAULT_ALBUMS,
    DEFAULT_ARTISTS,
    DEFAULT_GENRES,
    DEFAULT_HTTP,
    DEFAULT_KEYWORDS,
    DEFAULT_LIMIT,
    DEFAULT_LOCAL,
    DEFAULT_MAX_LENGTH,
    DEFAULT_MAX_RATING,
    DEFAULT_MAX_SIZE,
    DEFAULT_MIN_LENGTH,
    DEFAULT_MIN_RATING,
    DEFAULT_MIN_SIZE,
    DEFAULT_NAME,
    DEFAULT_NO_ALBUMS,
    DEFAULT_NO_ARTISTS,
    DEFAULT_NO_GENRES,
    DEFAULT_NO_KEYWORDS,
    DEFAULT_NO_TITLES,
    DEFAULT_SFTP,
    DEFAULT_SHUFFLE,
    DEFAULT_SPOTIFY,
    DEFAULT_TITLES,
    DEFAULT_YOUTUBE,
)
from musicbot.music_filter import MusicFilter

link_options = add_options(
    optgroup('Link options'),
    optgroup.option('--http/--no-http', is_flag=True, default=DEFAULT_HTTP),
    optgroup.option('--sftp/--no-sftp', is_flag=True, default=DEFAULT_SFTP),
    optgroup.option('--youtube/--no-youtube', is_flag=True, default=DEFAULT_YOUTUBE),
    optgroup.option('--spotify/--no-spotify', is_flag=True, default=DEFAULT_SPOTIFY),
    optgroup.option('--local/--no-local', is_flag=True, default=DEFAULT_LOCAL),
)


def sane_music_filter(ctx: click.Context, param: click.ParamType, value: Any) -> MusicFilter:  # pylint: disable=unused-argument
    kwargs: dict[str, Any] = {}
    for field in attr.fields_dict(MusicFilter):
        if isinstance(ctx.params[field], list):
            kwargs[field] = frozenset(ctx.params[field])
        else:
            kwargs[field] = ctx.params[field]
        ctx.params.pop(field)

    myfilter = MusicFilter(**kwargs)
    ctx.params[param.name] = myfilter
    return myfilter


shuffle_option = optgroup.option(
    '--shuffle',
    help='Randomize selection',
    default=DEFAULT_SHUFFLE,
    is_flag=True,
)

interleave_option = optgroup.option(
    '--interleave',
    help='Interleave tracks by artist',
    is_flag=True,
)

ordering_options = add_options(
    optgroup('Ordering options'),
    shuffle_option,
    interleave_option,
)

music_filter_options = add_options(
    optgroup('Filter options'),
    optgroup.option(
        '--name',
        help='Filter name',
        default=DEFAULT_NAME,
    ),
    optgroup.option(
        '--limit',
        help='Fetch a maximum limit of music',
        default=DEFAULT_LIMIT,
    ),
    shuffle_option,
    link_options,
    optgroup('Keywords'),
    optgroup.option(
        '--keywords',
        help='Select musics with keywords',
        multiple=True,
        default=DEFAULT_KEYWORDS,
        callback=split_arguments,
    ),
    optgroup.option(
        '--no-keywords',
        help='Filter musics without keywords',
        multiple=True,
        default=DEFAULT_NO_KEYWORDS,
        callback=split_arguments,
    ),
    optgroup('Artists'),
    optgroup.option(
        '--artists',
        help='Select musics with artists',
        multiple=True,
        default=DEFAULT_ARTISTS,
        callback=split_arguments,
    ),
    optgroup.option(
        '--no-artists',
        help='Filter musics without artists',
        multiple=True,
        default=DEFAULT_NO_ARTISTS,
        callback=split_arguments,
    ),
    optgroup('Albums'),
    optgroup.option(
        '--albums',
        help='Select musics with albums',
        multiple=True,
        default=DEFAULT_ALBUMS,
        callback=split_arguments,
    ),
    optgroup.option(
        '--no-albums',
        help='Filter musics without albums',
        multiple=True,
        default=DEFAULT_NO_ALBUMS,
        callback=split_arguments,
    ),
    optgroup('Titles'),
    optgroup.option(
        '--titles',
        help='Select musics with titles',
        multiple=True,
        default=DEFAULT_TITLES,
        callback=split_arguments,
    ),
    optgroup.option(
        '--no-titles',
        help='Filter musics without titless',
        multiple=True,
        default=DEFAULT_NO_TITLES,
        callback=split_arguments,
    ),
    optgroup('Genres'),
    optgroup.option(
        '--genres',
        help='Select musics with genres',
        multiple=True,
        default=DEFAULT_GENRES,
        callback=split_arguments,
    ),
    optgroup.option(
        '--no-genres',
        help='Filter musics without genres',
        multiple=True,
        default=DEFAULT_NO_GENRES,
        callback=split_arguments,
    ),
    optgroup('Length'),
    optgroup.option(
        '--min-length',
        help='Minimum length filter in seconds',
        default=DEFAULT_MIN_LENGTH,
    ),
    optgroup.option(
        '--max-length',
        help='Maximum length filter in seconds',
        default=DEFAULT_MAX_LENGTH,
    ),
    optgroup('Size'),
    optgroup.option(
        '--min-size',
        help='Minimum file size',
        default=DEFAULT_MIN_SIZE,
    ),
    optgroup.option(
        '--max-size',
        help='Maximum file size',
        default=DEFAULT_MAX_SIZE,
    ),
    optgroup('Rating'),
    optgroup.option(
        '--min-rating',
        help='Minimum rating',
        default=DEFAULT_MIN_RATING,
        show_default=True,
        type=click.FloatRange(DEFAULT_MIN_RATING, DEFAULT_MAX_RATING, clamp=True),
        callback=sane_rating,
    ),
    optgroup.option(
        '--max-rating',
        help='Maximum rating',
        default=DEFAULT_MAX_RATING,
        show_default=True,
        type=click.FloatRange(DEFAULT_MIN_RATING, DEFAULT_MAX_RATING, clamp=True),
        callback=sane_rating,
    ),
    optgroup.option(
        '--music-filter',
        help='Music Filter',
        expose_value=False,
        callback=sane_music_filter,
        hidden=True,
    ),
)
