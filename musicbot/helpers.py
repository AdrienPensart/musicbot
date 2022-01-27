from typing import Any
import logging
import functools
import getpass
import socket
import requests
from gql import gql
import humanize  # type: ignore
from musicbot.exceptions import MusicbotError, QuerySyntaxError

logger = logging.getLogger(__name__)


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def bytes_to_human(b: int) -> str:
    return str(humanize.naturalsize(b))


def parse_graphql(query: str) -> Any:
    try:
        gql(query)
    except Exception as e:
        raise QuerySyntaxError(f"Bad mutation : {query}") from e


@functools.lru_cache(maxsize=None)
def public_ip() -> str:
    try:
        return requests.get('https://api.ipify.org').text
    except Exception as e:  # pylint: disable=broad-except
        raise MusicbotError("Unable to detect Public IP") from e


@functools.lru_cache(maxsize=None)
def current_user() -> str:
    return getpass.getuser()
