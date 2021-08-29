from typing import TYPE_CHECKING, Collection, Iterable
import logging
import functools
import os
import getpass
import miniupnpc
import requests
from musicbot.object import MusicbotObject
from musicbot.timing import timeit
from musicbot.exceptions import MusicbotError
from musicbot.music.helpers import find_files, filecount

if TYPE_CHECKING:
    from musicbot.music.file import File


logger = logging.getLogger(__name__)


@timeit
def genfiles(folders: Iterable[str]) -> Collection["File"]:
    from musicbot.music.file import File, supported_formats
    directories = [os.path.abspath(f) for f in folders]
    count = 0
    for directory in directories:
        subcount = filecount(directory, supported_formats)
        logger.info(f"{directory} : file count: {subcount}")
        count += subcount

    file_list = find_files(folders, supported_formats)
    music_files = list(file_list)
    files = []

    def worker(file):
        try:
            m = File(file[1], file[0])
            files.append(m)
        except KeyboardInterrupt as e:
            logger.error(f'interrupted : {e}')
            raise
        except OSError as e:
            logger.error(e)
    MusicbotObject.parallel(worker, music_files)
    return files


@functools.lru_cache(maxsize=None)
def public_ip() -> str:
    try:
        return requests.get('https://checkip.amazonaws.com').text.strip()
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
