#!/usr/bin/env python3
'''Main module, import commands and start CLI'''
from typing import Any
import logging
import os
import sys
import requests
import spotipy  # type: ignore
import mutagen  # type: ignore
import click
from click_skeleton import skeleton, doc, backtrace, version_checker, helpers
import musicbot
from musicbot import version, exceptions
from musicbot.config import Conf, Config
from musicbot.cli.config import config_options
import musicbot.commands

PROG_NAME = "musicbot"
logger = logging.getLogger(__name__)

backtrace.hook(
    reverse=False,
    align=True,
    strip_path=False,
    enable_on_envvar_only=False,
    on_tty=False,
    conservative=False,
)


@skeleton(name=PROG_NAME, version=version.__version__, auto_envvar_prefix='MB')
@config_options
def cli(**kwargs) -> Any:
    """Music swiss knife, new gen."""
    Conf.config = Config(**kwargs)


@cli.command(short_help='Generates a README.rst', aliases=['doc'])
@click.pass_context
@click.option('--output', help='README output format', type=click.Choice(['rst', 'markdown']), default='rst', show_default=True)
def readme(ctx, output):
    '''Generates a complete readme'''
    doc.readme(cli, ctx.obj.prog_name, ctx.obj.context_settings, output)


cli.add_groups_from_package(musicbot.commands)


def main(**kwargs) -> int:
    helpers.raise_limits()
    check_version = helpers.str2bool(os.getenv('MB_CHECK_VERSION', 'true'))
    version_check = version_checker.VersionCheckerThread(
        prog_name=PROG_NAME,
        current_version=version.__version__,
        autostart=check_version,
    )
    exit_code = 1
    try:
        exit_code = cli.main(prog_name=PROG_NAME, **kwargs)
        return exit_code
    except (mutagen.MutagenError, exceptions.MusicbotError, spotipy.client.SpotifyException, requests.exceptions.ConnectionError) as e:
        logger.error(e)
        if Conf.config and Conf.config.debug:
            logger.exception(e)
    finally:
        version_check.print()
    return exit_code


if __name__ == '__main__':
    sys.exit(main())
