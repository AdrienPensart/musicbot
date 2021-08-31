from pathlib import Path
import click
from musicbot.cli.options import config_list

folder_argument = click.argument(
    'folder',
    type=click.Path(path_type=Path, exists=True, file_okay=False),
)

folders_argument = click.argument(
    'folders',
    type=click.Path(path_type=Path, exists=True, file_okay=False),
    nargs=-1,
    callback=config_list,
)

destination_argument = click.argument(
    'destination',
    type=click.Path(path_type=Path, exists=True, file_okay=False),
)
