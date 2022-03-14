from typing import Any

import click
from attr import fields_dict
from beartype import beartype
from click_option_group import optgroup  # type: ignore
from click_skeleton import add_options

from musicbot.link_options import (
    DEFAULT_HTTP,
    DEFAULT_LOCAL,
    DEFAULT_SFTP,
    DEFAULT_SPOTIFY,
    DEFAULT_YOUTUBE,
    LinkOptions
)


@beartype
def sane_link_options(ctx: click.Context, param: click.Parameter, value: Any) -> LinkOptions:  # pylint: disable=unused-argument
    if not param.name:
        raise click.Abort("No param name set")

    kwargs: dict[str, bool] = {}
    for field in fields_dict(LinkOptions):
        kwargs[field] = ctx.params[field]
        ctx.params.pop(field)

    link_options = LinkOptions(**kwargs)
    ctx.params[param.name] = link_options
    return link_options


link_options_options = add_options(
    optgroup('Link options'),
    optgroup.option(
        '--http/--no-http',
        help="Generate HTTP link",
        is_flag=True,
        default=DEFAULT_HTTP
    ),
    optgroup.option(
        '--sftp/--no-sftp',
        help="Generate sFTP link",
        is_flag=True,
        default=DEFAULT_SFTP
    ),
    optgroup.option(
        '--youtube/--no-youtube',
        help="Generate YouTube link",
        is_flag=True,
        default=DEFAULT_YOUTUBE
    ),
    optgroup.option(
        '--spotify/--no-spotify',
        help="Generate Spotify link",
        is_flag=True,
        default=DEFAULT_SPOTIFY
    ),
    optgroup.option(
        '--local/--no-local',
        help="Generate local link",
        is_flag=True,
        default=DEFAULT_LOCAL
    ),
    optgroup.option(
        '--link-options',
        help="Link options",
        expose_value=False,
        hidden=True,
        callback=sane_link_options
    ),
)
