import logging
from pathlib import Path

import click
from beartype import beartype
from click_option_group import optgroup  # type: ignore
from click_skeleton import add_options
from click_skeleton.helpers import split_arguments

from musicbot.cli.options import (
    config_string,
    dry_option,
    sane_rating,
    sane_set
)
from musicbot.defaults import (
    DEFAULT_ACOUSTID_API_KEY,
    DEFAULT_CHECKS,
    DEFAULT_FLAT,
    DEFAULT_MAX_RATING,
    DEFAULT_MIN_RATING
)
from musicbot.file import File

logger = logging.getLogger(__name__)

music_options_group = optgroup('Music options')
keywords_option = optgroup.option(
    '--keywords',
    help='Keywords',
    multiple=True,
    callback=split_arguments,
)
artist_option = optgroup.option('--artist', help='Artist')
album_option = optgroup.option('--album', help='Album')
title_option = optgroup.option('--title', help='Title')
genre_option = optgroup.option('--genre', help='Genre')
track_option = optgroup.option('--track', help='Track number')
rating_option = optgroup.option(
    '--rating',
    help='Rating',
    type=click.FloatRange(DEFAULT_MIN_RATING, DEFAULT_MAX_RATING, clamp=True),
    callback=sane_rating,
)

keywords_arguments = click.argument(
    'keywords',
    nargs=-1,
    callback=sane_set,
)

flat_option = click.option(
    '--flat',
    help="Do not create subfolders",
    is_flag=True,
    default=DEFAULT_FLAT,
)

file_options = add_options(
    music_options_group,
    keywords_option,
    artist_option,
    album_option,
    title_option,
    genre_option,
    track_option,
    rating_option,
)


@beartype
def sane_music(ctx: click.Context, param: click.Parameter, value: Path) -> File:
    if not param.name:
        raise click.Abort("no param name set")
    music = File.from_path(value)
    ctx.params['music'] = music
    return music


music_argument = add_options(
    dry_option,
    click.argument(
        'music',
        type=click.Path(
            path_type=Path,
            exists=True,
            dir_okay=False,
        ),
        callback=sane_music,
    )
)


def sane_paths(ctx: click.Context, param: click.Parameter, value: tuple[Path, ...]) -> list[Path]:
    '''Convert Tuple when multiple=True to a list'''
    if not param.name:
        raise click.Abort("no param name set")
    logger.debug(f"{param} : {value}")
    ctx.params[param.name] = list(value)
    return ctx.params[param.name]


paths_arguments = click.argument(
    'paths',
    type=click.Path(
        path_type=Path,
        exists=True,
        dir_okay=False,
    ),
    callback=sane_paths,
    nargs=-1,
)

checks_and_fix_options = add_options(
    optgroup('Check options'),
    optgroup.option(
        '--checks',
        help='Consistency tests',
        multiple=True,
        default=DEFAULT_CHECKS,
        show_default=True,
        type=click.Choice(DEFAULT_CHECKS),
        callback=split_arguments,
    ),
    optgroup.option(
        '--fix',
        help="Fix musics",
        is_flag=True,
    ),
)

acoustid_api_key_option = click.option(
    '--acoustid-api-key',
    help='AcoustID API Key',
    default=DEFAULT_ACOUSTID_API_KEY,
    callback=config_string,
)
