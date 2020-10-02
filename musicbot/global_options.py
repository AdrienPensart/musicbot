import click
from click_option_group import optgroup, MutuallyExclusiveOptionGroup  # type: ignore
from click_skeleton import ExpandedPath
from musicbot import defaults

config_option = optgroup.option(
    '--config', '-c',
    help='Config file path',
    type=ExpandedPath(writable=True, dir_okay=False),
    envvar=defaults.MB_CONFIG,
    default=defaults.DEFAULT_CONFIG,
    show_default=True,
)

log_option = optgroup.option(
    '--log', '-l',
    help='Log file path',
    type=ExpandedPath(writable=True, dir_okay=False),
    envvar=defaults.MB_LOG,
    default=defaults.DEFAULT_LOG,
)

debug_option = optgroup.option(
    '--debug',
    help='Same as "--verbosity debug"',
    envvar=defaults.MB_DEBUG,
    default=defaults.DEFAULT_DEBUG,
    is_flag=True,
)

info_option = optgroup.option(
    '--info',
    help='Same as "--verbosity info"',
    envvar=defaults.MB_INFO,
    default=defaults.DEFAULT_INFO,
    is_flag=True,
)

warning_option = optgroup.option(
    '--warning',
    help='Same as "--verbosity warning"',
    envvar=defaults.MB_WARNING,
    default=defaults.DEFAULT_WARNING,
    is_flag=True,
)

error_option = optgroup.option(
    '--error',
    help='Same as "--verbosity error"',
    envvar=defaults.MB_ERROR,
    default=defaults.DEFAULT_ERROR,
    is_flag=True,
)

critical_option = optgroup.option(
    '--critical',
    help='Same as "--verbosity critical"',
    envvar=defaults.MB_CRITICAL,
    default=defaults.DEFAULT_CRITICAL,
    is_flag=True,
)

timings_option = optgroup.option(
    '--timings', '-t',
    help='Set verbosity to info and show execution timings',
    envvar=defaults.MB_TIMINGS,
    default=defaults.DEFAULT_TIMINGS,
    is_flag=True,
    show_default=True,
)

verbosity_option = optgroup.option(
    '--verbosity',
    help='Set verbosity level',
    envvar=defaults.MB_VERBOSITY,
    default=defaults.DEFAULT_VERBOSITY,
    type=click.Choice(defaults.VERBOSITIES.keys()),
    show_default=True,
)

quiet_option = optgroup.option(
    '--quiet', '-q',
    help='Disable progress bars',
    envvar=defaults.MB_QUIET,
    default=defaults.DEFAULT_QUIET,
    is_flag=True,
    show_default=True,
)

options = [
    optgroup.group('Global options'),
    config_option,
    log_option,
    quiet_option,
    timings_option,
    optgroup('Verbosity', cls=MutuallyExclusiveOptionGroup),
    debug_option,
    info_option,
    warning_option,
    error_option,
    critical_option,
    verbosity_option,
]
