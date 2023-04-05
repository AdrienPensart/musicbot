import datetime as dt
import getpass
import logging
from functools import cache

import humanize
from beartype import beartype

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
def current_user() -> str:
    return getpass.getuser()
