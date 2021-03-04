import os
import logging
from typing import Optional, Any, Collection, Iterable
import click
from click_skeleton.helpers import mysplit
from musicbot import defaults
from musicbot.config import Conf
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
    type=click.Choice(['json', 'table', 'm3u']),
)


def config_string(ctx: click.Context, param: click.Parameter, value: Optional[str]) -> Any:
    arg_value = value
    logger.info(f"{param.name} : try string loading with arg value : {arg_value}")

    config_value = Conf.config.configfile.get('musicbot', param.name, fallback=None)
    logger.info(f"{param.name} : try string loading with config key : {config_value}")

    if arg_value:
        value = arg_value

    if config_value:
        if not value or value == param.default:
            value = config_value
        elif arg_value and arg_value != config_value:
            logger.warning(f"{param.name} : config string value {config_value} is not sync with arg value {arg_value}")

    if not value and param.required:
        raise click.BadParameter(f'missing string arg or config {param.name} in {Conf.config.config}', ctx, param, param.name)
    ctx.params[param.name] = value
    logger.info(f"{param.name} : string final value {value}")
    return value


def config_list(ctx: click.Context, param: click.Parameter, value: Any) -> Any:
    arg_value = value
    logger.info(f"{param.name} : try list loading with arg value : {arg_value}")

    config_value = Conf.config.configfile.get('musicbot', param.name, fallback=None)
    list_value = tuple(mysplit(config_value, ',')) if config_value is not None else []
    logger.info(f"{param.name} : try list loading with config key : {list_value}")

    if arg_value:
        value = arg_value

    if list_value:
        if not value or value == param.default:
            value = list_value
        elif arg_value and arg_value != list_value:
            logger.warning(f"{param.name} : config list value {list_value} is not sync with arg value {arg_value}")

    if not value and param.required:
        raise click.BadParameter(f'missing list arg or config {param.name} in {Conf.config.config}', ctx, param, param.name)
    logger.info(f"{param.name} : list final value {value}")
    ctx.params[param.name] = value
    return value


@Conf.timeit
def genfiles(folders: Iterable[str]) -> Collection[File]:
    directories = [os.path.abspath(f) for f in folders]
    count = 0
    for directory in directories:
        subcount = filecount(directory, supported_formats)
        logger.info(f"{directory} : file count: {subcount}")
        count += subcount

    file_list = find_files(folders, supported_formats)
    music_files = list(file_list)
    files = []

    def worker(file):
        try:
            m = File(file[1], file[0])
            files.append(m)
        except KeyboardInterrupt as e:
            logger.error(f'interrupted : {e}')
            raise
        except OSError as e:
            logger.error(e)
    Conf.parallel(worker, music_files)
    return files


folders_argument = click.argument(
    'folders',
    type=click.Path(exists=True, file_okay=False),
    nargs=-1,
    callback=config_list,
)

folder_argument = click.argument(
    'folder',
    type=click.Path(exists=True, file_okay=False),
)
