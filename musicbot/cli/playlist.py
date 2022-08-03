import click
from click_option_group import optgroup  # type: ignore
from click_skeleton import add_options
from click_skeleton.helpers import split_arguments

from musicbot.defaults import DEFAULT_LINK, LINK_CHOICES

links_option = click.option(
    '--link', '--links',
    'links',
    help="Generate playlist link of kind",
    multiple=True,
    default=DEFAULT_LINK,
    show_default=True,
    type=click.Choice(LINK_CHOICES),
    callback=split_arguments,
)

bests_options = add_options(
    optgroup.group("Bests options"),
    optgroup.option(
        '--min-playlist-size',
        help="Minimum size of playlist to write",
        default=1
    ),
)
