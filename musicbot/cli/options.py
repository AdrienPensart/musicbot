import logging
from typing import Optional, Any
import click
from click_skeleton.helpers import mysplit
from musicbot.defaults import DEFAULT_MB_CONCURRENCY, DEFAULT_DRY, DEFAULT_SAVE, DEFAULT_MB_OUTPUT, DEFAULT_YES
from musicbot.config import Conf

logger = logging.getLogger(__name__)

concurrency_options = click.option(
    '--concurrency',
    help='Number of threads',
    default=DEFAULT_MB_CONCURRENCY,
    show_default=True,
)

dry_option = click.option(
    '--dry',
    help='Take no real action',
    default=DEFAULT_DRY,
    is_flag=True,
    show_default=True,
)

yes_option = click.option(
    '--yes', '-y',
    help='Confirm action',
    default=DEFAULT_YES,
    is_flag=True,
)

save_option = click.option(
    '--save', '-s',
    help='Save to config file',
    default=DEFAULT_SAVE,
    is_flag=True,
    show_default=True,
)

output_option = click.option(
    '--output',
    help='Output format',
    default=DEFAULT_MB_OUTPUT,
    show_default=True,
    type=click.Choice(['json', 'table', 'm3u']),
)


def config_string(ctx: click.Context, param: click.Parameter, value: Optional[str]) -> Any:
    arg_value = value
    logger.info(f"{param.name} : try string loading with arg value : {arg_value}")

    if param.name:
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

    if param.name:
        ctx.params[param.name] = value
    logger.info(f"{param.name} : string final value {value}")
    return value


def config_list(ctx: click.Context, param: click.Parameter, value: Any) -> Any:
    arg_value = value
    logger.info(f"{param.name} : try list loading with arg value : {arg_value}")

    if param.name:
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
    if param.name:
        ctx.params[param.name] = value
    return value


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
