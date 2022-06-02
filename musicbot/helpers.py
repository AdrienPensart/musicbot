import datetime as dt
import getpass
import logging
from functools import cache

import humanize  # type: ignore
import requests
from beartype import beartype

from musicbot.exceptions import MusicbotError

logger = logging.getLogger(__name__)


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
