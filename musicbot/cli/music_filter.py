import logging
from typing import Any

import click
from attr import fields
from click_skeleton.helpers import mysplit

from musicbot.music_filter import MusicFilter
from musicbot.object import MusicbotObject

logger = logging.getLogger(__name__)


def sane_music_filters(ctx: click.Context, param: click.Parameter, value: Any) -> list[MusicFilter]:
    '''Convert a list of <key>=<value> to a dict'''
    if not param.name:
        logger.error('no option name')
        raise click.Abort()
    if value is None:
        return []

    and_filters = []
    for val in value:
        properties = {}
        for comma_separated in mysplit(val, ","):
            if '=' not in comma_separated:
                MusicbotObject.err('Error with a property, there is no "=" between key and value (<key>=<value>)')
                raise click.Abort()
            split_val = [x for x in comma_separated.split('=', 1) if x]
            if len(split_val) != 2:
                MusicbotObject.err(f'Error with a property, splitted value should be of length 2 : {split_val}')
                raise click.Abort()

            properties[split_val[0]] = split_val[1]
        mf = MusicFilter(**properties)
        and_filters.append(mf)

    ctx.params[param.name] = and_filters
    return ctx.params[param.name]


fields_names = ','.join([field.name for field in fields(MusicFilter)])

music_filters_option = click.option(
    '--filter',
    'music_filters',
    help=f"Music filters (repeatable), fields: {fields_names}",
    multiple=True,
    callback=sane_music_filters,
)
