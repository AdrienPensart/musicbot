import click
from click_option_group import optgroup  # type: ignore
from click_skeleton import add_options

from musicbot.cli.options import sane_list
from musicbot.defaults import (
    DEFAULT_MAX_RATING,
    DEFAULT_MIN_RATING,
    DEFAULT_RATINGS
)

bests_options = add_options(
    optgroup.group("Bests options"),
    optgroup.option(
        '--min-playlist-size',
        help="Minimum size of playlist to write",
        default=1
    ),
    optgroup.option(
        '--rating',
        'ratings',
        help="Generate bests for those ratings",
        default=DEFAULT_RATINGS,
        type=click.FloatRange(DEFAULT_MIN_RATING, DEFAULT_MAX_RATING, clamp=True),
        multiple=True,
    ),
    optgroup.option(
        '--types',
        help="Type of bests playlists",
        default=["genre", "keyword", "rating", "artist"],
        multiple=True,
        callback=sane_list
    ),
)
