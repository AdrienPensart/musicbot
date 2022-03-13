import getpass
import logging
import socket
from functools import cache
from typing import Sequence

import humanize  # type: ignore
import requests

from musicbot.exceptions import MusicbotError

logger = logging.getLogger(__name__)


def approx_chunks(lst: Sequence, n: int) -> list[Sequence]:
    '''Cut a list in chunks of approximative equal length'''
    k, m = divmod(len(lst), n)
    return [lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def bytes_to_human(b: int) -> str:
    return str(humanize.naturalsize(b))


@cache
def public_ip() -> str:
    try:
        return requests.get('https://api.ipify.org').text
    except Exception as e:  # pylint: disable=broad-except
        raise MusicbotError("Unable to detect Public IP") from e


@cache
def current_user() -> str:
    return getpass.getuser()
