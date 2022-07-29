from click_option_group import optgroup  # type: ignore
from click_skeleton import add_options

bests_options = add_options(
    optgroup.group("Bests options"),
    optgroup.option(
        '--min-playlist-size',
        help="Minimum size of playlist to write",
        default=1
    ),
)
