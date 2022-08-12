import logging
from typing import Any

import click
from attrs import fields
from click_option_group import (  # type: ignore
    MutuallyExclusiveOptionGroup,
    optgroup
)
from click_skeleton import add_options
from click_skeleton.helpers import split_arguments

from musicbot.defaults import (
    DEFAULT_INTERLEAVE,
    DEFAULT_KINDS,
    DEFAULT_RELATIVE,
    DEFAULT_SHUFFLE,
    KINDS_CHOICES
)
from musicbot.playlist_options import PlaylistOptions

logger = logging.getLogger(__name__)


bests_options = add_options(
    optgroup.group("Bests options"),
    optgroup.option(
        '--min-playlist-size',
        help="Minimum size of playlist to write",
        default=1
    ),
)


def sane_playlist_options(ctx: click.Context, param: click.Parameter, value: str | None) -> PlaylistOptions:  # pylint: disable=unused-argument
    if not param.name:
        logger.error("no param name set")
        raise click.Abort()

    kwargs: dict[str, Any] = {}
    for field in fields(PlaylistOptions):  # pylint: disable=not-an-iterable
        kwargs[field.name] = ctx.params[field.name]
        ctx.params.pop(field.name)

    playlist_options = PlaylistOptions(**kwargs)
    ctx.params[param.name] = playlist_options
    return playlist_options


playlist_options = add_options(
    optgroup('Links options'),
    optgroup.option(
        '--kind', '--kinds',
        'kinds',
        help="Generate musics paths of types",
        multiple=True,
        default=list(DEFAULT_KINDS),
        show_default=True,
        type=click.Choice(list(KINDS_CHOICES)),
        callback=split_arguments,
    ),
    optgroup.option(
        '--relative/--no-relative',
        help='Generate relative links',
        default=DEFAULT_RELATIVE,
        show_default=True,
        is_flag=True,
    ),
    optgroup('Ordering options', cls=MutuallyExclusiveOptionGroup),
    optgroup.option(
        '--shuffle/--no-shuffle',
        help='Randomize selection',
        default=DEFAULT_SHUFFLE,
        show_default=True,
        is_flag=True,
    ),
    optgroup.option(
        '--interleave/--no-interleave',
        help='Interleave tracks by artist',
        default=DEFAULT_INTERLEAVE,
        show_default=True,
        is_flag=True,
    ),
    optgroup('Playlist object'),
    optgroup.option(
        '--playlist-options',
        help='Playlist Options',
        expose_value=False,
        callback=sane_playlist_options,
        hidden=True,
    ),
)
