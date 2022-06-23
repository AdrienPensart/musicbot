import asyncio
import datetime as dt
import getpass
import logging
import warnings
from functools import cache
from typing import Any, Callable

import humanize
import requests
from beartype import beartype

from musicbot.exceptions import MusicbotError

logger = logging.getLogger(__name__)


@cache
def async_loop() -> Any:
    try:
        loop = asyncio.get_running_loop()
        if loop.is_running():
            return loop
    except RuntimeError:
        pass
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop


def async_run(fn: Any) -> Any:
    loop = async_loop()
    return loop.run_until_complete(fn)


def async_gather(fn: Any, objects: Any, callback: Callable | None = None) -> Any:
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        loop = async_loop()
        futures = []
        for o in objects:
            coroutine = fn(o)
            future = asyncio.ensure_future(coroutine)
            if callback:
                future.add_done_callback(callback)
            futures.append(future)

        final_future = asyncio.gather(*futures)
        return loop.run_until_complete(final_future)


@beartype
def bytes_to_human(b: int) -> str:
    return str(humanize.naturalsize(b))


@beartype
def precise_seconds_to_human(s: int) -> str:
    delta = dt.timedelta(seconds=s)
    return humanize.precisedelta(delta)


@cache
@beartype
def get_public_ip() -> str:
    try:
        return requests.get('https://api.ipify.org').text
    except Exception as e:  # pylint: disable=broad-except
        raise MusicbotError("Unable to detect Public IP") from e


@cache
@beartype
def current_user() -> str:
    return getpass.getuser()
