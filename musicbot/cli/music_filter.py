import logging
from typing import Any

import click
from attr import evolve, fields
from click_option_group import optgroup  # type: ignore
from click_skeleton import add_options
from click_skeleton.helpers import split_arguments

from musicbot.cli.options import sane_rating
from musicbot.defaults import (
    DEFAULT_ALBUMS,
    DEFAULT_ARTISTS,
    DEFAULT_GENRES,
    DEFAULT_KEYWORDS,
    DEFAULT_LIMIT,
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
    DEFAULT_TITLES
)
from musicbot.music_filter import DEFAULT_FILTERS, MusicFilter

logger = logging.getLogger(__name__)


def sane_music_filter(ctx: click.Context, param: click.Parameter, value: str | None) -> MusicFilter:  # pylint: disable=unused-argument
    if not param.name:
        logger.error("no param name set")
        raise click.Abort()

    name = ctx.params.pop('name', None)
    rating = ctx.params.pop('rating', None)

    kwargs: dict[str, Any] = {}
    for field in fields(MusicFilter):  # pylint: disable=not-an-iterable
        if isinstance(ctx.params[field.name], list) and ctx.params[field.name] != field.default:
            kwargs[field.name] = frozenset(ctx.params[field.name])
        elif ctx.params[field.name] != field.default:
            kwargs[field.name] = ctx.params[field.name]
        ctx.params.pop(field.name)

    if rating is not None:
        kwargs['min_rating'] = rating
        kwargs['max_rating'] = rating

    if name is not None:
        music_filter = DEFAULT_FILTERS[name]
        music_filter = evolve(music_filter, **kwargs)
    else:
        music_filter = MusicFilter(**kwargs)
    ctx.params[param.name] = music_filter
    return music_filter


music_filter_options = add_options(
    optgroup('Filter options'),
    optgroup.option(
        '--name',
        help='Filter name',
        type=click.Choice(list(DEFAULT_FILTERS.keys())),
        default=DEFAULT_NAME,
    ),
    optgroup.option(
        '--limit',
        help='Fetch a maximum limit of music',
        default=DEFAULT_LIMIT,
    ),
    optgroup('Keywords'),
    optgroup.option(
        '--keywords', '--keyword',
        'keywords',
        help='Select musics with keywords',
        multiple=True,
        default=DEFAULT_KEYWORDS,
        callback=split_arguments,
    ),
    optgroup.option(
        '--no-keywords', '--no-keyword',
        'no_keywords',
        help='Filter musics without keywords',
        multiple=True,
        default=DEFAULT_NO_KEYWORDS,
        callback=split_arguments,
    ),
    optgroup('Artists'),
    optgroup.option(
        '--artists', '--artist',
        'artists',
        help='Select musics with artists',
        multiple=True,
        default=DEFAULT_ARTISTS,
        callback=split_arguments,
    ),
    optgroup.option(
        '--no-artists', '--no-artist',
        'no_artists',
        help='Filter musics without artists',
        multiple=True,
        default=DEFAULT_NO_ARTISTS,
        callback=split_arguments,
    ),
    optgroup('Albums'),
    optgroup.option(
        '--albums', '--album',
        'albums',
        help='Select musics with albums',
        multiple=True,
        default=DEFAULT_ALBUMS,
        callback=split_arguments,
    ),
    optgroup.option(
        '--no-albums', '--no-album',
        'no_albums',
        help='Filter musics without albums',
        multiple=True,
        default=DEFAULT_NO_ALBUMS,
        callback=split_arguments,
    ),
    optgroup('Titles'),
    optgroup.option(
        '--titles', '--title',
        'titles',
        help='Select musics with titles',
        multiple=True,
        default=DEFAULT_TITLES,
        callback=split_arguments,
    ),
    optgroup.option(
        '--no-titles', '--no-title',
        'no_titles',
        help='Filter musics without titless',
        multiple=True,
        default=DEFAULT_NO_TITLES,
        callback=split_arguments,
    ),
    optgroup('Genres'),
    optgroup.option(
        '--genres', '--genre',
        'genres',
        help='Select musics with genres',
        multiple=True,
        default=DEFAULT_GENRES,
        callback=split_arguments,
    ),
    optgroup.option(
        '--no-genres', '--no-genre',
        'no_genres',
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
        '--rating',
        help='Fixed rating',
        type=click.FloatRange(DEFAULT_MIN_RATING, DEFAULT_MAX_RATING, clamp=True),
        callback=sane_rating,
    ),
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
