import logging
from pathlib import Path

import click
from beartype import beartype
from click_option_group import optgroup
from click_skeleton import add_options

from musicbot.cli.options import config_list, dry_option, sane_frozenset
from musicbot.defaults import DEFAULT_EXTENSIONS
from musicbot.scan_folders import ScanFolders

logger = logging.getLogger(__name__)


@beartype
def sane_scan_folders(ctx: click.Context, param: click.Parameter, value: tuple[str, ...]) -> ScanFolders:
    if not param.name:
        logger.error("no param name set")
        raise click.Abort()
    value = config_list(ctx, param, value)
    limit = ctx.params.pop("limit", None)
    extensions = ctx.params.pop("extensions", DEFAULT_EXTENSIONS)
    paths = [Path(path) for path in value]
    folders = ScanFolders(
        directories=paths,
        limit=limit,
        extensions=extensions,
    )
    ctx.params[param.name] = folders
    return folders


scan_folder_argument = click.argument(
    "scan_folder",
    type=click.Path(
        path_type=Path,
        exists=True,
        file_okay=False,
    ),
)

scan_folders_argument = add_options(
    dry_option,
    optgroup.group("Folders options"),
    optgroup.option(
        "--limit",
        help="Limit number of music files",
        type=int,
        is_eager=True,
    ),
    optgroup.option(
        "--extension",
        "extensions",
        help="Supported formats",
        default=sorted(DEFAULT_EXTENSIONS),
        multiple=True,
        callback=sane_frozenset,
        show_default=True,
        is_eager=True,
    ),
    click.argument(
        "scan_folders",
        nargs=-1,
        callback=sane_scan_folders,
    ),
)


destination_argument = click.argument(
    "destination",
    type=click.Path(
        path_type=Path,
        exists=True,
        file_okay=False,
    ),
)
