from pathlib import Path

import click
from beartype import beartype
from click_option_group import optgroup  # type: ignore
from click_skeleton import add_options
from click_skeleton.helpers import split_arguments

from musicbot.cli.options import config_list, dry_option
from musicbot.defaults import DEFAULT_EXTENSIONS
from musicbot.folders import Folders


@beartype
def sane_folders(ctx: click.Context, param: click.Parameter, value: tuple[str, ...]) -> Folders:
    if not param.name:
        raise click.Abort("no param name set")
    value = config_list(ctx, param, value)
    limit = ctx.params.pop('limit', None)
    extensions = ctx.params.pop('extensions', DEFAULT_EXTENSIONS)
    paths = [Path(path) for path in value]
    folders = Folders(
        directories=paths,
        limit=limit,
        extensions=extensions,
    )
    ctx.params[param.name] = folders
    return folders


folder_argument = click.argument(
    'folder',
    type=click.Path(
        path_type=Path,
        exists=True,
        file_okay=False,
    )
)

folders_argument = add_options(
    dry_option,
    optgroup.group("Folders options"),
    optgroup.option(
        '--limit',
        help="Limit number of music files",
        type=int,
        is_eager=True,
    ),
    optgroup.option(
        '--extension',
        'extensions',
        help='Supported formats',
        default=DEFAULT_EXTENSIONS,
        multiple=True,
        callback=split_arguments,
        is_eager=True,
    ),
    click.argument(
        'folders',
        nargs=-1,
        callback=sane_folders,
    )
)


destination_argument = click.argument(
    'destination',
    type=click.Path(
        path_type=Path,
        exists=True,
        file_okay=False,
    ),
)
