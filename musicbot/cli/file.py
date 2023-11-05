import functools
import logging
from pathlib import Path
from typing import Any

import click
from beartype import beartype
from click_option_group import optgroup
from click_skeleton import add_options
from click_skeleton.helpers import split_arguments

from musicbot.cli.options import config_string, dry_option, sane_rating, sane_set
from musicbot.cli.scan_folders import scan_folder_argument
from musicbot.defaults import (
    DEFAULT_ACOUSTID_API_KEY,
    DEFAULT_FLAT,
    DEFAULT_MAX_RATING,
    DEFAULT_MIN_RATING,
)
from musicbot.file import File

logger = logging.getLogger(__name__)

keywords_option = click.option(
    "--keywords",
    help="Keywords",
    multiple=True,
    callback=sane_set,
)

keywords_arguments = click.argument(
    "keywords",
    nargs=-1,
    callback=sane_set,
)

flat_option = click.option(
    "--flat",
    help="Do not create subfolders",
    is_flag=True,
    default=DEFAULT_FLAT,
    show_default=True,
)

file_options = add_options(
    optgroup("Music options"),
    optgroup.option(
        "--keywords",
        help="Keywords",
        multiple=True,
        callback=split_arguments,
    ),
    optgroup.option("--artist", help="Artist"),
    optgroup.option("--album", help="Album"),
    optgroup.option("--title", help="Title"),
    optgroup.option("--genre", help="Genre"),
    optgroup.option("--track", help="Track number"),
    optgroup.option(
        "--rating",
        help="Rating",
        type=click.FloatRange(DEFAULT_MIN_RATING, DEFAULT_MAX_RATING, clamp=True),
        callback=sane_rating,
    ),
)


@beartype
def file_argument(func: Any) -> Any:
    """Generates a valid list of Instance objects"""

    @scan_folder_argument
    @click.argument(
        "file",
        type=click.Path(
            path_type=Path,
            exists=True,
            dir_okay=False,
        ),
    )
    @dry_option
    @functools.wraps(func)
    def wrapper(scan_folder: Path, file: Path, *args: Any, **kwargs: Any) -> Any:
        if music_file := File.from_path(folder=scan_folder, path=file):
            return func(file=music_file, *args, **kwargs)
        raise click.Abort()

    return wrapper


def sane_paths(ctx: click.Context, param: click.Parameter, value: tuple[Path, ...]) -> list[Path]:
    """Convert Tuple when multiple=True to a list"""
    if not param.name:
        logger.error("no param name set")
        raise click.Abort()
    logger.debug(f"{param} : {value}")
    ctx.params[param.name] = list(value)
    return ctx.params[param.name]


paths_arguments = click.argument(
    "paths",
    type=click.Path(
        path_type=Path,
        exists=True,
        dir_okay=False,
    ),
    callback=sane_paths,
    nargs=-1,
)

acoustid_api_key_option = click.option(
    "--acoustid-api-key",
    help="AcoustID API Key",
    default=DEFAULT_ACOUSTID_API_KEY,
    callback=config_string,
)
