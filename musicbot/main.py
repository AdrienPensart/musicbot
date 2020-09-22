#!/usr/bin/env python3
'''Main module, import commands and start CLI'''
import logging
import sys
import requests
import spotipy  # type: ignore
import mutagen  # type: ignore

from click_skeleton import backtrace, version_checker, helpers
from musicbot.config import config as config_obj
from musicbot.cli import main_cli, PROG_NAME, __version__
from musicbot import exceptions

logger = logging.getLogger(__name__)

backtrace.hook(
    reverse=False,
    align=True,
    strip_path=False,
    enable_on_envvar_only=False,
    on_tty=False,
    conservative=False,
)


def main(**kwargs):
    helpers.raise_limits()
    from musicbot import commands
    logger.debug(f"Imported commands: {commands.modules}")
    version_check = version_checker.VersionCheckerThread(
        prog_name=PROG_NAME,
        current_version=__version__,
        autostart=config_obj.check_version,
    )
    try:
        exit_code = main_cli.main(**kwargs)
        version_check.print()
        return exit_code
    except (mutagen.MutagenError, exceptions.MusicbotError, spotipy.client.SpotifyException, requests.exceptions.ConnectionError) as e:
        if config_obj.debug:
            logger.exception(e)
        else:
            raise


if __name__ == '__main__':
    sys.exit(main())
