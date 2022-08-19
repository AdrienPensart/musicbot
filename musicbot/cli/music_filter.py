import logging
from typing import Any

import click
from attr import evolve, fields
from click_option_group import optgroup  # type: ignore
from click_skeleton import add_options

from musicbot.cli.options import sane_rating
from musicbot.defaults import (
    DEFAULT_LIMIT,
    DEFAULT_MAX_LENGTH,
    DEFAULT_MAX_RATING,
    DEFAULT_MAX_SIZE,
    DEFAULT_MIN_LENGTH,
    DEFAULT_MIN_RATING,
    DEFAULT_MIN_SIZE,
    MATCH_ALL
)
from musicbot.music_filter import DEFAULT_PRE_FILTERS, MusicFilter

logger = logging.getLogger(__name__)


def sane_music_filter(ctx: click.Context, param: click.Parameter, value: str | None) -> MusicFilter:  # pylint: disable=unused-argument
    if not param.name:
        logger.error("no param name set")
        raise click.Abort()

    prefilter = ctx.params.pop('prefilter', None)
    rating = ctx.params.pop('rating', None)

    kwargs: dict[str, Any] = {}
    for field in fields(MusicFilter):  # pylint: disable=not-an-iterable
        if ctx.params[field.name] != field.default:
            kwargs[field.name] = ctx.params[field.name]
        ctx.params.pop(field.name)

    if rating is not None:
        kwargs['min_rating'] = rating
        kwargs['max_rating'] = rating

    if prefilter is not None:
        music_filter = DEFAULT_PRE_FILTERS[prefilter]
        music_filter = evolve(music_filter, **kwargs)
    else:
        music_filter = MusicFilter(**kwargs)
    ctx.params[param.name] = music_filter
    return music_filter


music_filter_options = add_options(
    optgroup('Filter options'),
    optgroup.option(
        '--prefilter',
        help='Filter name',
        type=click.Choice(list(sorted(DEFAULT_PRE_FILTERS.keys()))),
        show_default=True,
    ),
    optgroup.option(
        '--limit',
        help='Fetch a maximum limit of music',
        default=DEFAULT_LIMIT,
        show_default=True,
    ),
    optgroup.option(
        '--keywords', '--keyword',
        'keyword',
        help='Select musics with keyword regex',
        default=MATCH_ALL,
        show_default=True,
    ),
    optgroup.option(
        '--artists', '--artist',
        'artist',
        help='Select musics with artist regex',
        default=MATCH_ALL,
        show_default=True,
    ),
    optgroup.option(
        '--albums', '--album',
        'album',
        help='Select musics with album regex',
        default=MATCH_ALL,
        show_default=True,
    ),
    optgroup.option(
        '--titles', '--title',
        'title',
        help='Select musics with title regex',
        default=MATCH_ALL,
        show_default=True,
    ),
    optgroup.option(
        '--genres', '--genre',
        'genre',
        help='Select musics with genre regex',
        default=MATCH_ALL,
        show_default=True,
    ),
    optgroup('Length'),
    optgroup.option(
        '--min-length',
        help='Minimum length filter in seconds',
        default=DEFAULT_MIN_LENGTH,
        show_default=True,
    ),
    optgroup.option(
        '--max-length',
        help='Maximum length filter in seconds',
        default=DEFAULT_MAX_LENGTH,
        show_default=True,
    ),
    optgroup('Size'),
    optgroup.option(
        '--min-size',
        help='Minimum file size',
        default=DEFAULT_MIN_SIZE,
        show_default=True,
    ),
    optgroup.option(
        '--max-size',
        help='Maximum file size',
        default=DEFAULT_MAX_SIZE,
        show_default=True,
    ),
    optgroup('Rating'),
    optgroup.option(
        '--rating',
        help='Fixed rating',
        type=click.FloatRange(DEFAULT_MIN_RATING, DEFAULT_MAX_RATING, clamp=True),
        callback=sane_rating,
        show_default=True,
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
