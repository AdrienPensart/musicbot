from pathlib import Path

import click
from click_option_group import optgroup  # type: ignore
from click_skeleton import add_options
from click_skeleton.helpers import split_arguments

from musicbot.cli.options import (
    config_string,
    sane_list,
    sane_rating,
)
from musicbot.defaults import (
    DEFAULT_ACOUSTID_API_KEY,
    DEFAULT_CHECKS,
    DEFAULT_EXTENSIONS,
    DEFAULT_FLAT,
    DEFAULT_MIN_RATING,
    DEFAULT_MAX_RATING,
)

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

extensions_option = click.option(
    '--extension',
    'extensions',
    help='Supported formats',
    default=DEFAULT_EXTENSIONS,
    multiple=str,
    callback=sane_list,
)

keywords_argument = click.argument(
    'keywords',
    nargs=-1,
    callback=split_arguments,
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

path_argument = click.argument(
    'path',
    type=click.Path(
        path_type=Path,
        exists=True,
        dir_okay=False,
    ),
)

paths_arguments = click.argument(
    'paths',
    type=click.Path(
        path_type=Path,
        exists=True,
        dir_okay=False,
    ),
    callback=sane_list,
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
        callback=sane_list,
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
