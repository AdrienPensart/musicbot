import logging

import click
from beartype import beartype
from beartype.typing import Any
from click_skeleton.helpers import mysplit

from musicbot.defaults import (
    DEFAULT_CLEAN,
    DEFAULT_COROUTINES,
    DEFAULT_DRY,
    DEFAULT_OUTPUT,
    DEFAULT_SAVE,
    DEFAULT_THREADS,
    DEFAULT_YES,
    RATING_CHOICES,
)
from musicbot.object import MusicbotObject

logger = logging.getLogger(__name__)


@beartype
def sane_dry(ctx: click.Context, param: click.Parameter, value: bool) -> None:  # pylint: disable=unused-argument
    """Overwrite global dry mode"""
    if not param.name:
        logger.error("no param name set")
        raise click.Abort()
    # this value can only go from False to True
    if not MusicbotObject.dry and value is True:
        MusicbotObject.dry.set_mode(value)


dry_option = click.option(
    "--dry/--no-dry",
    help="Do not launch real action",
    is_flag=True,
    default=DEFAULT_DRY,
    show_default=True,
    callback=sane_dry,
    expose_value=False,
)


@beartype
def sane_coroutines(ctx: click.Context, param: click.Parameter, value: int) -> None:  # pylint: disable=unused-argument
    """Overwrite global concurrency"""
    if not param.name:
        logger.error("no param name set")
        raise click.Abort()
    MusicbotObject.coroutines = value


coroutines_option = click.option(
    "--coroutines",
    help="Limit number of coroutines",
    default=DEFAULT_COROUTINES,
    callback=sane_coroutines,
    show_default=True,
    expose_value=False,
)

true_values = ("enabled", "y", "yes", "t", "true", "on", "1")
false_values = ("", "none", "disabled", "n", "no", "f", "false", "off", "0")


@beartype
def sane_rating(ctx: click.Context, param: click.Parameter, value: float | None) -> float | None:
    if not param.name:
        logger.error("no param name set")
        raise click.Abort()
    if value is not None:
        if value not in RATING_CHOICES:
            raise ValueError(f"Invalid rating choice {value}, it should be in {RATING_CHOICES}")
    elif param.required:
        raise ValueError("Rating is mandatory")
    ctx.params[param.name] = value
    return value


@beartype
def str2bool(val: Any) -> bool:
    """Converts any value to string and detects if it looks like a known bool value"""
    val = str(val).lower()
    if val in true_values:
        return True
    if val in false_values:
        return False
    raise ValueError(f"invalid truth value {val}")


@beartype
def yes_or_no(question: str, default: str | None = "no") -> bool:
    """Re-implement click.confirm but do not ask confirmation if we are in a script"""
    if not MusicbotObject.is_tty:
        print("Y/N : non interactive shell detected, answer is NO")
        return False

    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError(f"Unknown setting '{default}' for default.")

    while True:
        try:
            MusicbotObject.echo(question + prompt, fg="bright_magenta")
            resp = input()  # nosec
            if default is not None and resp == "":
                return default == "yes"
            return str2bool(resp)
        except ValueError:
            print("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")


@beartype
def sane_list(ctx: click.Context, param: click.Parameter, value: Any) -> list[Any]:
    """Convert Tuple when multiple=True to a List"""
    if not param.name:
        logger.error("no option name")
        raise click.Abort()
    final_values = []
    for one_value in value:
        if isinstance(one_value, str):
            final_values.extend(mysplit(one_value))
        else:
            final_values.append(one_value)
    ctx.params[param.name] = final_values
    return ctx.params[param.name]


@beartype
def sane_frozenset(ctx: click.Context, param: click.Parameter, value: Any) -> frozenset[Any]:
    """Convert Tuple when multiple=True to a Set"""
    if not param.name:
        logger.error("no option name")
        raise click.Abort()
    final_values = set()
    for one_value in value:
        if isinstance(one_value, str):
            final_values.update(mysplit(one_value))
        else:
            final_values.add(one_value)
    ctx.params[param.name] = frozenset(final_values)
    return ctx.params[param.name]


@beartype
def sane_set(ctx: click.Context, param: click.Parameter, value: Any) -> set[Any]:
    """Convert Tuple when multiple=True to a Set"""
    if not param.name:
        logger.error("no option name")
        raise click.Abort()
    final_values = set()
    for one_value in value:
        if isinstance(one_value, str):
            final_values.update(mysplit(one_value))
        else:
            final_values.add(one_value)
    ctx.params[param.name] = set(final_values)
    return ctx.params[param.name]


@beartype
def confirm(ctx: click.Context, param: Any, value: bool) -> None:  # pylint: disable=unused-argument
    """Callback to confirm action of user"""
    if not (value or MusicbotObject.dry or yes_or_no("Do you REALLY want to confirm ?")):
        raise click.Abort()


yes_option = click.option(
    "--yes",
    "-y",
    help="Confirm action",
    default=DEFAULT_YES,
    is_flag=True,
    show_default=True,
    expose_value=False,
    callback=confirm,
)

open_option = click.option(
    "--open/--no-open",
    "_open",
    is_flag=True,
    default=True,
    show_default=True,
)

lazy_yes_option = click.option(
    "--yes",
    "-y",
    help="Confirm action",
    is_flag=True,
)

clean_option = click.option(
    "--clean",
    help="Delete musics before",
    default=DEFAULT_CLEAN,
    is_flag=True,
    show_default=True,
)

threads_option = click.option(
    "--threads",
    help="Number of threads",
    default=DEFAULT_THREADS,
    show_default=True,
)

save_option = click.option(
    "--save",
    "-s",
    help="Save to config file",
    default=DEFAULT_SAVE,
    is_flag=True,
    show_default=True,
)

output_option = click.option(
    "--output",
    help="Output format",
    default=DEFAULT_OUTPUT,
    show_default=True,
    type=click.Choice(["json", "table", "m3u"]),
)


@beartype
def config_string(ctx: click.Context, param: click.Parameter, value: str | None) -> Any:
    arg_value = value
    logger.info(f"{param.name} : try string loading with arg value : {arg_value}")

    config_value = None
    if param.name:
        config_value = MusicbotObject.config.configfile.get("musicbot", param.name, fallback=None)
        logger.info(f"{param.name} : try string loading with config key from {MusicbotObject.config.config} : {config_value}")

    if arg_value:
        value = arg_value

    if config_value:
        if not value or value == param.default:
            value = config_value
        elif arg_value and arg_value != config_value:
            logger.warning(f"{param.name} : config string value {config_value} is not sync with arg value {arg_value}")

    if not value and param.required:
        raise click.BadParameter(f"missing string arg or config {param.name} in {MusicbotObject.config.config}", ctx, param, param.name)

    value = param.type(value)
    if param.name:
        ctx.params[param.name] = value
    logger.info(f"{param.name} : string final value {value}")
    return value


@beartype
def config_list(ctx: click.Context, param: click.Parameter, value: Any) -> Any:
    value = sane_list(ctx, param, value)
    arg_value = value
    list_value = []
    logger.info(f"{param.name} : try list loading with arg value : {arg_value}")

    if param.name:
        config_value = MusicbotObject.config.configfile.get("musicbot", param.name, fallback=None)
        if config_value:
            for v in mysplit(config_value, ","):
                try:
                    list_value.append(param.type(v))
                except Exception as e:
                    logger.warning(e)
        logger.info(f"{param.name} : try list loading with config key : {list_value}")

    if arg_value:
        value = arg_value

    if list_value:
        if not value or value == param.default:
            value = list_value
        elif arg_value and arg_value != list_value:
            logger.warning(f"{param.name} : config list value {list_value} is not sync with arg value {arg_value}")

    if not value and param.required:
        raise click.BadParameter(f"missing list arg or config {param.name} in {MusicbotObject.config.config}", ctx, param, param.name)
    logger.info(f"{param.name} : list final value {value}")
    if param.name:
        ctx.params[param.name] = value
    return value
