import getpass
import logging
import socket
from functools import lru_cache

import humanize  # type: ignore
import requests

from musicbot.exceptions import MusicbotError

logger = logging.getLogger(__name__)


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def bytes_to_human(b: int) -> str:
    return str(humanize.naturalsize(b))


@lru_cache(maxsize=None)
def public_ip() -> str:
    try:
        return requests.get('https://api.ipify.org').text
    except Exception as e:  # pylint: disable=broad-except
        raise MusicbotError("Unable to detect Public IP") from e


@lru_cache(maxsize=None)
def current_user() -> str:
    return getpass.getuser()
