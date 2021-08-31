import logging
from typing import Optional, Any
import click
from click_skeleton.helpers import mysplit
from musicbot.defaults import DEFAULT_MB_CONCURRENCY, DEFAULT_DRY, DEFAULT_SAVE, DEFAULT_MB_OUTPUT, DEFAULT_YES
from musicbot.object import MusicbotObject

logger = logging.getLogger(__name__)


def sane_dry(ctx, param, value):  # pylint: disable=unused-argument
    '''Overwrite global dry mode'''
    MusicbotObject.dry = value


dry_option = click.option(
    '--dry/--no-dry',
    help='Do not launch real action',
    is_flag=True,
    default=DEFAULT_DRY,
    show_default=True,
    callback=sane_dry,
    expose_value=False,
    is_eager=True,
)

true_values = ('enabled', 'y', 'yes', 't', 'true', 'True', 'on', '1')
false_values = ('', 'none', 'disabled', 'n', 'no', 'f', 'false', 'False', 'off', '0')


def str2bool(val: Any) -> bool:
    '''Converts any value to string and detects if it looks like a known bool value'''
    val = str(val).lower()
    if val in true_values:
        return True
    if val in false_values:
        return False
    raise ValueError(f"invalid truth value {val}")


def yes_or_no(question: str, default='no'):
    '''Re-implement click.confirm but do not ask confirmation if we are in a script'''
    if not MusicbotObject.is_tty:
        print("Y/N : non interactive shell detected, answer is NO")
        return False

    if default is None:
        prompt = " [y/n] "
    elif default == 'yes':
        prompt = " [Y/n] "
    elif default == 'no':
        prompt = " [y/N] "
    else:
        raise ValueError(f"Unknown setting '{default}' for default.")

    while True:
        try:
            MusicbotObject.echo(question + prompt, fg="bright_magenta")
            resp = input()  # nosec
            if default is not None and resp == '':
                return default == 'yes'
            return str2bool(resp)
        except ValueError:
            print("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")


def confirm(ctx, param, value):  # pylint: disable=unused-argument
    '''Callback to confirm action of user'''
    if not (value or MusicbotObject.dry or yes_or_no('Do you REALLY want to confirm ?')):
        raise click.Abort()


yes_option = click.option(
    '--yes', '-y',
    help='Confirm action',
    default=DEFAULT_YES,
    is_flag=True,
    show_default=True,
    expose_value=False,
    callback=confirm,
)

concurrency_options = click.option(
    '--concurrency',
    help='Number of threads',
    default=DEFAULT_MB_CONCURRENCY,
    show_default=True,
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
        config_value = MusicbotObject.config.configfile.get('musicbot', param.name, fallback=None)
        logger.info(f"{param.name} : try string loading with config key from {MusicbotObject.config.config} : {config_value}")

    if arg_value:
        value = arg_value

    if config_value:
        if not value or value == param.default:
            value = config_value
        elif arg_value and arg_value != config_value:
            logger.warning(f"{param.name} : config string value {config_value} is not sync with arg value {arg_value}")

    if not value and param.required:
        raise click.BadParameter(f'missing string arg or config {param.name} in {MusicbotObject.config.config}', ctx, param, param.name)

    value = param.type(value)
    if param.name:
        ctx.params[param.name] = value
    logger.info(f"{param.name} : string final value {value}")
    return value


def config_list(ctx: click.Context, param: click.Parameter, value: Any) -> Any:
    arg_value = value
    logger.info(f"{param.name} : try list loading with arg value : {arg_value}")

    if param.name:
        config_value = MusicbotObject.config.configfile.get('musicbot', param.name, fallback=None)
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
        raise click.BadParameter(f'missing list arg or config {param.name} in {MusicbotObject.config.config}', ctx, param, param.name)
    logger.info(f"{param.name} : list final value {value}")
    value = [param.type(v) for v in value]
    if param.name:
        ctx.params[param.name] = value
    return value
