from pathlib import Path
import click
from click_option_group import optgroup  # type: ignore
from click_skeleton import add_options
from musicbot.defaults import DEFAULT_FLAT, DEFAULT_EXTENSIONS
from musicbot.music.file import DEFAULT_CHECKS, DEFAULT_ACOUSTID_API_KEY
from musicbot.cli.options import config_string

music_options_group = optgroup('Music options')
keywords_option = optgroup.option('--keywords', help='Keywords', multiple=True)
artist_option = optgroup.option('--artist', help='Artist')
album_option = optgroup.option('--album', help='Album')
title_option = optgroup.option('--title', help='Title')
genre_option = optgroup.option('--genre', help='Genre')
number_option = optgroup.option('--number', help='Track number')
rating_option = optgroup.option('--rating', help='Rating')

extensions_option = click.option(
    '--extension',
    'extensions',
    help='Supported formats',
    default=DEFAULT_EXTENSIONS,
    multiple=str,
)

keywords_argument = click.argument(
    'keywords',
    nargs=-1,
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
    number_option,
    rating_option,
)

path_argument = click.argument(
    'path',
    type=click.Path(path_type=Path, exists=True, dir_okay=False),
)

link_options = add_options(
    optgroup('Link options'),
    optgroup.option('--http/--no-http', is_flag=True),
    optgroup.option('--sftp/--no-sftp', is_flag=True),
    optgroup.option('--youtube/--no-youtube', is_flag=True),
    optgroup.option('--spotify/--no-spotify', is_flag=True),
    optgroup.option('--local/--no-local', is_flag=True, default=True),
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
