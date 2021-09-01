import logging
import functools
import getpass
import miniupnpc  # type: ignore
import requests
from gql import gql  # type: ignore
import humanize  # type: ignore
from musicbot.object import MusicbotObject
from musicbot.exceptions import MusicbotError, QuerySyntaxError

logger = logging.getLogger(__name__)


def bytes_to_human(b: int) -> str:
    return str(humanize.naturalsize(b))


def parse_graphql(query):
    try:
        gql(query)
    except Exception as e:
        raise QuerySyntaxError(f"Bad mutation : {query}") from e


@functools.lru_cache(maxsize=None)
def public_ip() -> str:
    try:
        return requests.get('https://api.ipify.org').text
    except Exception as e:  # pylint: disable=broad-except
        MusicbotObject.warn(f"Unable to detect public IP via Amazon : {e}")

    try:
        upnp = miniupnpc.UPnP()
        upnp.discoverdelay = 200
        upnp.discover()
        upnp.selectigd()
        return upnp.externalipaddress()
    except Exception as e:  # pylint: disable=broad-except
        MusicbotObject.warn(f"Unable to detect public IP via UPnP : {e}")

    raise MusicbotError("Unable to detect Public IP")


@functools.lru_cache(maxsize=None)
def current_user():
    return getpass.getuser()
