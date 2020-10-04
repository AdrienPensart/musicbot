import os
import logging
from typing import Any, Collection, Iterable
import click
from click_skeleton.helpers import mysplit
from musicbot import defaults
from musicbot.config import config
from musicbot.music.file import File, supported_formats
from musicbot.music.helpers import find_files, filecount

logger = logging.getLogger(__name__)

concurrency_options = click.option(
    '--concurrency',
    help='Number of coroutines',
    default=defaults.DEFAULT_MB_CONCURRENCY,
    show_default=True,
)

dry_option = click.option(
    '--dry',
    help='Take no real action',
    default=defaults.DEFAULT_DRY,
    is_flag=True,
    show_default=True,
)

yes_option = click.option(
    '--yes', '-y',
    help='Confirm action',
    default=defaults.DEFAULT_YES,
    is_flag=True,
)

save_option = click.option(
    '--save', '-s',
    help='Save to config file',
    default=defaults.DEFAULT_SAVE,
    is_flag=True,
    show_default=True,
)

output_option = click.option(
    '--output',
    help='Output format',
    default=defaults.DEFAULT_MB_OUTPUT,
    show_default=True,
    type=click.Choice(['table', 'json']),
)

playlist_output_option = click.option(
    '--output',
    help='Output format',
    default=defaults.DEFAULT_MB_PLAYLIST_OUTPUT,
    show_default=True,
    type=click.Choice(['json', 'm3u', 'table']),
)


def config_string(ctx: click.Context, param: Any, value: Any) -> Any:
    arg_value = value
    logger.info(f"{param.name} : try loading with value : {value}")

    config_value = config.configfile.get('musicbot', param.name, fallback=None)
    logger.info(f"{param.name} : try loading with config key : {config_value}")

    if arg_value:
        value = arg_value

    if config_value:
        if not value or value == param.default:
            value = config_value
        elif arg_value and arg_value != config_value:
            logger.warning(f"{param.name} : config value {config_value} is not sync with arg value {arg_value}")

    if not value and param.required:
        raise click.BadParameter(f'missing arg or config {param.name} in {config.config}', ctx, param.name, param.name)
    logger.info(f"{param.name} : final value {value}")
    ctx.params[param.name] = value
    return value


def config_list(ctx: click.Context, param: Any, value: Any) -> Any:
    arg_value = value
    logger.info(f"{param.name} : try loading with value : {value}")

    config_value = config.configfile.get('musicbot', param.name, fallback=None)
    list_value = tuple(mysplit(config_value, ',')) if config_value is not None else []
    logger.info(f"{param.name} : try loading with config key : {list_value}")

    if arg_value:
        value = arg_value

    if list_value:
        if not value or value == param.default:
            value = list_value
        elif arg_value and arg_value != list_value:
            logger.warning(f"{param.name} : config value {list_value} is not sync with arg value {arg_value}")

    if not value and param.required:
        raise click.BadParameter(f'missing arg or config {param.name} in {config.config}', ctx, param.name, param.name)
    logger.info(f"{param.name} : final value {value}")
    ctx.params[param.name] = value
    return value


@config.timeit
def genfiles(folders: Iterable[str]) -> Collection[File]:
    directories = [os.path.abspath(f) for f in folders]
    count = 0
    for directory in directories:
        subcount = filecount(directory, supported_formats)
        logger.info(f"{directory} : file count: {subcount}")
        count += subcount

    files = []
    file_list = find_files(folders, supported_formats)
    music_files = list(file_list)

    with config.progressbar(max_value=len(music_files), redirect_stdout=True) as pbar:
        for f in music_files:
            try:
                m = File(f[1], f[0])
                files.append(m)
            except OSError as e:
                logger.error(e)
            finally:
                pbar.value += 1
                pbar.update()
    return files


folders_argument = click.argument(
    'folders',
    nargs=-1,
    callback=config_list,
    type=click.Path(exists=True, file_okay=False),
)
