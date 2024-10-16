import logging
from dataclasses import fields, replace

import click
from beartype.typing import Any
from click_option_group import optgroup
from click_skeleton import add_options
from click_skeleton.helpers import mysplit

from musicbot.music_filter import DEFAULT_PREFILTERS, MusicFilter
from musicbot.object import MusicbotObject

logger = logging.getLogger(__name__)

NAME_TO_FIELD = {field.name: field for field in fields(MusicFilter)}
JOINED_FIELDS_NAMES = ",".join(NAME_TO_FIELD.keys())  # pylint: disable=not-an-iterable
FILTERS_REPRS = """\b
""" + "\n".join(
    [f"{k}: {v.help_repr()}" for k, v in DEFAULT_PREFILTERS.items()]
)


def sane_music_filters(ctx: click.Context, param: click.Parameter, value: Any) -> list[MusicFilter]:
    """Convert a list of <key>=<value> to a dict"""
    if not param.name:
        logger.error("no option name")
        raise click.Abort()
    if value is None:
        return []

    and_filters = []
    prefilters = ctx.params.pop("music_prefilters", [])
    for prefilter in prefilters:
        if prefilter in DEFAULT_PREFILTERS:
            and_filters.append(DEFAULT_PREFILTERS[prefilter])
        else:
            MusicbotObject.err(f"Unknown prefilter {prefilter}")
            raise click.Abort()

    for val in value:
        mf = MusicFilter()
        for comma_separated in mysplit(val, ","):
            if "=" not in comma_separated:
                MusicbotObject.err('Error with a property, there is no "=" between key and value (<key>=<value>)')
                raise click.Abort()
            split_val = [x for x in comma_separated.split("=", 1) if x]
            if len(split_val) != 2:
                MusicbotObject.err(f"Error with a property, splitted value should be of length 2 : {split_val}")
                raise click.Abort()

            property_key = split_val[0]
            property_value: str | int | float = split_val[1]

            field = NAME_TO_FIELD.get(property_key, None)
            if field is None:
                MusicbotObject.err(f"Error : unknown property {property_key} for value {property_value}")
                raise click.Abort()

            mf = replace(mf, **{field.name: field.type(property_value)})  # type: ignore

        and_filters.append(mf)

    if not and_filters:
        and_filters.append(MusicFilter())
    ctx.params[param.name] = and_filters
    return ctx.params[param.name]


music_filters_options = add_options(
    optgroup("Filter options"),
    optgroup.option(
        "--prefilter",
        "music_prefilters",
        help="Music pre filters (repeatable)",
        type=click.Choice(list(sorted(DEFAULT_PREFILTERS.keys()))),
        show_default=True,
        expose_value=False,
        multiple=True,
    ),
    optgroup.option(
        "--filter",
        "music_filters",
        help=f"Music filters (repeatable), fields: {JOINED_FIELDS_NAMES}",
        multiple=True,
        callback=sane_music_filters,
    ),
)
