import logging
from typing import Any

import click
from attr import fields_dict
from beartype import beartype
from click_option_group import optgroup  # type: ignore
from click_skeleton import add_options

from musicbot.link_options import (  # DEFAULT_SPOTIFY,; DEFAULT_YOUTUBE,
    DEFAULT_HTTP,
    DEFAULT_LOCAL,
    DEFAULT_SFTP,
    LinkOptions
)

logger = logging.getLogger(__name__)


@beartype
def sane_link_options(ctx: click.Context, param: click.Parameter, value: Any) -> LinkOptions:  # pylint: disable=unused-argument
    if not param.name:
        logger.error("No param name set")
        raise click.Abort()

    kwargs: dict[str, Any] = {}
    for field in fields_dict(LinkOptions):
        if field not in ctx.params:
            logger.debug(f"{field} param not in options")
            continue
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
        default=DEFAULT_HTTP,
        show_default=True,
    ),
    optgroup.option(
        '--sftp/--no-sftp',
        help="Generate sFTP link",
        is_flag=True,
        default=DEFAULT_SFTP,
        show_default=True,
    ),
    # optgroup.option(
    #     '--youtube/--no-youtube',
    #     help="Generate YouTube link",
    #     is_flag=True,
    #     default=DEFAULT_YOUTUBE,
    #     show_default=True,
    # ),
    # optgroup.option(
    #     '--spotify/--no-spotify',
    #     help="Generate Spotify link",
    #     is_flag=True,
    #     default=DEFAULT_SPOTIFY,
    #     show_default=True,
    # ),
    optgroup.option(
        '--local/--no-local',
        help="Generate local link",
        is_flag=True,
        default=DEFAULT_LOCAL,
        show_default=True,
    ),
    optgroup.option(
        '--link-options',
        help="Link options",
        expose_value=False,
        hidden=True,
        callback=sane_link_options
    ),
)
