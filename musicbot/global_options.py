import click
from click_option_group import optgroup, MutuallyExclusiveOptionGroup  # type: ignore
from click_skeleton import ExpandedPath
from musicbot.config import (
    VERBOSITIES,
    DEFAULT_QUIET,
    DEFAULT_CONFIG,
    DEFAULT_LOG,
    DEFAULT_VERBOSITY,
    DEFAULT_DEBUG,
    DEFAULT_INFO,
    DEFAULT_WARNING,
    DEFAULT_ERROR,
    DEFAULT_CRITICAL,
    DEFAULT_TIMINGS,

    MB_CONFIG,
    MB_LOG,
    MB_DEBUG,
    MB_INFO,
    MB_WARNING,
    MB_ERROR,
    MB_CRITICAL,
    MB_TIMINGS,
    MB_VERBOSITY,
    MB_QUIET,
)


config_option = [
    optgroup.option(
        '--config', '-c',
        help='Config file path',
        type=ExpandedPath(writable=True, dir_okay=False),
        envvar=MB_CONFIG,
        default=DEFAULT_CONFIG,
        show_default=True,
    )
]

log_option = [
    optgroup.option(
        '--log', '-l',
        help='Log file path',
        type=ExpandedPath(writable=True, dir_okay=False),
        envvar=MB_LOG,
        default=DEFAULT_LOG,
    )
]

debug_option = [
    optgroup.option(
        '--debug',
        help='Same as "--verbosity debug"',
        envvar=MB_DEBUG,
        default=DEFAULT_DEBUG,
        is_flag=True,
    )
]

info_option = [
    optgroup.option(
        '--info',
        help='Same as "--verbosity info"',
        envvar=MB_INFO,
        default=DEFAULT_INFO,
        is_flag=True,
    )
]

warning_option = [
    optgroup.option(
        '--warning',
        help='Same as "--verbosity warning"',
        envvar=MB_WARNING,
        default=DEFAULT_WARNING,
        is_flag=True,
    )
]

error_option = [
    optgroup.option(
        '--error',
        help='Same as "--verbosity error"',
        envvar=MB_ERROR,
        default=DEFAULT_ERROR,
        is_flag=True,
    )
]

critical_option = [
    optgroup.option(
        '--critical',
        help='Same as "--verbosity critical"',
        envvar=MB_CRITICAL,
        default=DEFAULT_CRITICAL,
        is_flag=True,
    )
]

timings_option = [
    optgroup.option(
        '--timings', '-t',
        help='Set verbosity to info and show execution timings',
        envvar=MB_TIMINGS,
        default=DEFAULT_TIMINGS,
        is_flag=True,
        show_default=True,
    )
]

verbosity_option = [
    optgroup.option(
        '--verbosity',
        help='Set verbosity level',
        envvar=MB_VERBOSITY,
        default=DEFAULT_VERBOSITY,
        type=click.Choice(VERBOSITIES.keys()),
        show_default=True,
    )
]

quiet_option = [
    optgroup.option(
        '--quiet', '-q',
        help='Disable progress bars',
        envvar=MB_QUIET,
        default=DEFAULT_QUIET,
        is_flag=True,
        show_default=True,
    )
]

options =\
    [optgroup.group('Global options')] +\
    config_option +\
    log_option +\
    quiet_option +\
    timings_option +\
    [optgroup('Verbosity', cls=MutuallyExclusiveOptionGroup)] +\
    debug_option +\
    info_option +\
    warning_option +\
    error_option +\
    critical_option +\
    verbosity_option
