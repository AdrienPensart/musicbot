import click
from click_option_group import (  # type: ignore
    MutuallyExclusiveOptionGroup,
    optgroup
)
from click_skeleton import add_options

from musicbot.config import (
    DEFAULT_COLOR,
    DEFAULT_CONFIG,
    DEFAULT_CRITICAL,
    DEFAULT_DEBUG,
    DEFAULT_ERROR,
    DEFAULT_INFO,
    DEFAULT_LOG,
    DEFAULT_QUIET,
    DEFAULT_WARNING
)

config_option = optgroup.option(
    '--config', '-c',
    help='Config file path',
    type=click.Path(readable=True, writable=True, dir_okay=False),
    envvar='MB_CONFIG',
    default=DEFAULT_CONFIG,
    show_default=True,
)

color_option = optgroup.option(
    '--color/--no-color',
    help='Enable or disable color in output',
    envvar='MB_COLOR',
    is_flag=True,
    default=DEFAULT_COLOR,
    show_default=True,
)

log_option = optgroup.option(
    '--log', '-l',
    help='Log file path',
    type=click.Path(writable=True, dir_okay=False),
    envvar='MB_LOG',
    default=DEFAULT_LOG,
    show_default=True,
)

debug_option = optgroup.option(
    '--debug',
    help='Debug verbosity',
    envvar='MB_DEBUG',
    default=DEFAULT_DEBUG,
    is_flag=True,
)

info_option = optgroup.option(
    '--info',
    help='Info verbosity',
    envvar='MB_INFO',
    default=DEFAULT_INFO,
    is_flag=True,
)

warning_option = optgroup.option(
    '--warning',
    help='Warning verbosity',
    envvar='MB_WARNING',
    default=DEFAULT_WARNING,
    is_flag=True,
)

error_option = optgroup.option(
    '--error',
    help='Error verbosity',
    envvar='MB_ERROR',
    default=DEFAULT_ERROR,
    is_flag=True,
)

critical_option = optgroup.option(
    '--critical',
    help='Critical verbosity',
    envvar='MB_CRITICAL',
    default=DEFAULT_CRITICAL,
    is_flag=True,
)

quiet_option = optgroup.option(
    '-q', '--quiet/--no-quiet',
    help='Disable progress bars',
    envvar='MB_QUIET',
    default=DEFAULT_QUIET,
    is_flag=True,
    show_default=True,
)

config_options = add_options(
    optgroup('Global options'),
    config_option,
    log_option,
    quiet_option,
    color_option,
    optgroup('Verbosity', cls=MutuallyExclusiveOptionGroup),
    debug_option,
    info_option,
    warning_option,
    error_option,
    critical_option,
)
