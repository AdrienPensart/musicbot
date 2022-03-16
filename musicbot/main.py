#!/usr/bin/env python3
'''Main module, import commands and start CLI'''
import logging
import os
import sys
from typing import Any, Final

import click
import edgedb
import mutagen  # type: ignore
import requests
import spotipy  # type: ignore
from beartype import beartype
from click_skeleton import backtrace, doc, helpers, skeleton, version_checker

import musicbot
import musicbot.commands
from musicbot import Config, MusicbotObject, exceptions, version
from musicbot.cli.config import config_options
from musicbot.cli.options import dry_option

PROG_NAME: Final[str] = "musicbot"
logger = logging.getLogger(__name__)

backtrace.hook(strip_path=False, enable_on_envvar_only=False, on_tty=False)


@skeleton(name=PROG_NAME, version=version.__version__, auto_envvar_prefix='MB')
@click.pass_context
@config_options
@dry_option
@beartype
def cli(
    ctx: click.Context,
    log: str | None,
    color: bool,
    quiet: bool,
    debug: bool,
    info: bool,
    warning: bool,
    error: bool,
    critical: bool,
    config: str,
) -> Any:
    """Music swiss knife, new gen."""
    MusicbotObject.config = Config(
        log=log,
        color=color,
        quiet=quiet,
        debug=debug,
        info=info,
        warning=warning,
        error=error,
        critical=critical,
        config=config,
    )
    ctx.color = MusicbotObject.config.color


@cli.command(short_help='Generates a README.rst', aliases=['doc'])
@click.pass_context
@click.option('--output', help='README output format', type=click.Choice(['rst', 'markdown']), default='rst', show_default=True)
def readme(ctx: click.Context, output: str) -> None:
    '''Generates a complete readme'''
    doc.readme(cli, ctx.obj.prog_name, ctx.obj.context_settings, output)


cli.add_groups_from_package(musicbot.commands)


def main(**kwargs: Any) -> int:
    helpers.raise_limits()
    check_version = helpers.str2bool(os.environ.get('MB_CHECK_VERSION', MusicbotObject.is_prod()))
    version_check = version_checker.VersionCheckerThread(
        prog_name=PROG_NAME,
        current_version=version.__version__,
        autostart=check_version,
    )
    exit_code = 1
    try:
        exit_code = cli.main(prog_name=PROG_NAME, **kwargs)
        return exit_code
    except (
        mutagen.MutagenError,
        exceptions.MusicbotError,
        spotipy.client.SpotifyException,
        requests.exceptions.ConnectionError,
        edgedb.errors.AuthenticationError
    ) as e:
        logger.error(e)
        if MusicbotObject.config and MusicbotObject.config.debug:
            logger.exception(e)
    finally:
        version_check.print()
    return exit_code


if __name__ == '__main__':
    sys.exit(main())
