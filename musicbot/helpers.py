import asyncio
import datetime as dt
import getpass
import logging
from collections.abc import Callable, Coroutine
from functools import cache, partial, wraps
from typing import Any, ParamSpec, TypeVar

import humanize
from beartype import beartype

logger = logging.getLogger(__name__)
T_Retval = TypeVar("T_Retval")
T_ParamSpec = ParamSpec("T_ParamSpec")
T = TypeVar("T")


@beartype
def bytes_to_human(b: int) -> str:
    return str(humanize.naturalsize(b))


@beartype
def precise_seconds_to_human(s: int) -> str:
    delta = dt.timedelta(seconds=s)
    return humanize.precisedelta(delta)


@cache
@beartype
def current_user() -> str:
    return getpass.getuser()


def syncify(
    async_function: Callable[T_ParamSpec, Coroutine[Any, Any, T_Retval]],
) -> Callable[T_ParamSpec, T_Retval]:
    """Run an async task"""

    @wraps(async_function)
    def wrapper(*args: T_ParamSpec.args, **kwargs: T_ParamSpec.kwargs) -> T_Retval:
        partial_f = partial(async_function, *args, **kwargs)
        with asyncio.Runner() as runner:
            return runner.run(partial_f())

    return wrapper
