from typing import Any
import click
import attr
from click_option_group import optgroup  # type: ignore
from musicbot.music import music_filter
from musicbot.music.music_filter import MusicFilter


def sane_rating(ctx: click.Context, param: click.ParamType, value: float) -> float:
    if value in music_filter.rating_choices:
        ctx.params[param.name] = value
        return value
    return float('nan')


def sane_filter(ctx: click.Context, param: click.ParamType, value: Any) -> MusicFilter:  # pylint: disable=unused-argument
    kwargs = {}
    for field in attr.fields_dict(music_filter.MusicFilter):
        kwargs[field] = ctx.params[field]
        ctx.params.pop(field)

    myfilter = music_filter.MusicFilter(**kwargs)
    ctx.params['music_filter'] = myfilter
    return myfilter


options = [
    optgroup.group('Filter options'),
    optgroup.option(
        '--music-filter',
        help='Music Filter',
        expose_value=False,
        callback=sane_filter,
        hidden=True,
    ),
    optgroup.option(
        '--name',
        help='Filter name',
        default=music_filter.default_name,
        is_eager=True,
    ),
    optgroup.option(
        '--limit',
        help='Fetch a maximum limit of music',
        default=music_filter.default_limit,
        is_eager=True,
    ),
    optgroup.option(
        '--youtubes',
        help='Select musics with a youtube link',
        multiple=True,
        default=music_filter.default_youtubes,
        is_eager=True,
    ),
    optgroup.option(
        '--no-youtubes',
        help='Select musics without youtube link',
        multiple=True,
        default=music_filter.default_no_youtubes,
        is_eager=True,
    ),
    optgroup.option(
        '--spotifys',
        help='Select musics with a spotifys link',
        multiple=True,
        default=music_filter.default_youtubes,
        is_eager=True,
    ),
    optgroup.option(
        '--no-spotifys',
        help='Select musics without spotifys link',
        multiple=True,
        default=music_filter.default_no_youtubes,
        is_eager=True,
    ),
    optgroup.option(
        '--formats',
        help='Select musics with file format',
        multiple=True,
        default=music_filter.default_formats,
        is_eager=True,
    ),
    optgroup.option(
        '--no-formats',
        help='Filter musics without format',
        multiple=True,
        default=music_filter.default_no_formats,
        is_eager=True,
    ),
    optgroup.option(
        '--keywords',
        help='Select musics with keywords',
        multiple=True,
        default=music_filter.default_keywords,
        is_eager=True,
    ),
    optgroup.option(
        '--no-keywords',
        help='Filter musics without keywords',
        multiple=True,
        default=music_filter.default_no_keywords,
        is_eager=True,
    ),
    optgroup.option(
        '--artists',
        help='Select musics with artists',
        multiple=True,
        default=music_filter.default_artists,
        is_eager=True,
    ),
    optgroup.option(
        '--no-artists',
        help='Filter musics without artists',
        multiple=True,
        default=music_filter.default_no_artists,
        is_eager=True,
    ),
    optgroup.option(
        '--albums',
        help='Select musics with albums',
        multiple=True,
        default=music_filter.default_albums,
        is_eager=True,
    ),
    optgroup.option(
        '--no-albums',
        help='Filter musics without albums',
        multiple=True,
        default=music_filter.default_no_albums,
        is_eager=True,
    ),
    optgroup.option(
        '--titles',
        help='Select musics with titles',
        multiple=True,
        default=music_filter.default_titles,
        is_eager=True,
    ),
    optgroup.option(
        '--no-titles',
        help='Filter musics without titless',
        multiple=True,
        default=music_filter.default_no_titles,
        is_eager=True,
    ),
    optgroup.option(
        '--genres',
        help='Select musics with genres',
        multiple=True,
        default=music_filter.default_genres,
        is_eager=True,
    ),
    optgroup.option(
        '--no-genres',
        help='Filter musics without genres',
        multiple=True,
        default=music_filter.default_no_genres,
        is_eager=True,
    ),
    optgroup.option(
        '--min-duration',
        help='Minimum duration filter (hours:minutes:seconds)',
        default=music_filter.default_min_duration,
        is_eager=True,
    ),
    optgroup.option(
        '--max-duration',
        help='Maximum duration filter (hours:minutes:seconds))',
        default=music_filter.default_max_duration,
        is_eager=True,
    ),
    optgroup.option(
        '--min-size',
        help='Minimum file size filter (in bytes)',
        default=music_filter.default_min_size,
        is_eager=True,
    ),
    optgroup.option(
        '--max-size',
        help='Maximum file size filter (in bytes)',
        default=music_filter.default_max_size,
        is_eager=True,
    ),
    optgroup.option(
        '--min-rating',
        help='Minimum rating',
        default=music_filter.default_min_rating,
        show_default=True,
        callback=sane_rating,
        is_eager=True,
    ),
    optgroup.option(
        '--max-rating',
        help='Maximum rating',
        default=music_filter.default_max_rating,
        show_default=True,
        callback=sane_rating,
        is_eager=True,
    ),
    optgroup.option(
        '--relative',
        help='Generate relatives paths',
        default=music_filter.default_relative,
        is_flag=True,
        is_eager=True,
    ),
    optgroup.option(
        '--shuffle',
        help='Randomize selection',
        default=music_filter.default_shuffle,
        is_flag=True,
        is_eager=True,
    ),
]
