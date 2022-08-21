#!/usr/bin/env python3
'''Main module, import commands and start CLI'''
import gc
import logging
import os
from typing import Any, Final

import click
import edgedb
import mutagen  # type: ignore
import requests
import spotipy  # type: ignore
import uvloop
from beartype import beartype
from click_skeleton import backtrace, doc, helpers, skeleton, version_checker

import musicbot
import musicbot.commands
from musicbot import Config, MusicbotObject, version
# from musicbot.helpers import async_run
from musicbot.cli.config import config_options
from musicbot.cli.options import dry_option
from musicbot.exceptions import MusicbotError

PROG_NAME: Final[str] = "musicbot"
logger = logging.getLogger(__name__)


@skeleton(
    name=PROG_NAME,
    version=version.__version__,
    auto_envvar_prefix='MB',
    groups_package=musicbot.commands
)
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
    backtrace.hook(strip_path=False, enable_on_envvar_only=False, on_tty=False)
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
    if not MusicbotObject.config.quiet and not MusicbotObject.is_test():
        import progressbar  # type: ignore
        progressbar.streams.wrap(stderr=True, stdout=True)


@cli.command(short_help='Generates a README.rst', aliases=['doc'])
@click.pass_context
@click.option('--output', help='README output format', type=click.Choice(['rst', 'markdown']), default='rst', show_default=True)
def readme(ctx: click.Context, output: str) -> None:
    '''Generates a complete readme'''
    doc.readme(cli, ctx.obj.prog_name, ctx.obj.context_settings, output)


def main() -> None:
    uvloop.install()
    if not helpers.raise_limits():
        MusicbotObject.err("unable to raise ulimit")

    disable_gc: bool = helpers.str2bool(os.environ.get('MB_DISABLE_GC', False))
    if disable_gc:
        gc.disable()

    check_version = helpers.str2bool(os.environ.get('MB_CHECK_VERSION', MusicbotObject.is_prod()))
    version_check = version_checker.VersionCheckerThread(
        prog_name=PROG_NAME,
        current_version=version.__version__,
        autostart=check_version,
    )
    try:
        cli.main(prog_name=PROG_NAME, standalone_mode=False)
    except (KeyboardInterrupt, click.exceptions.Abort):
        pass
    except click.ClickException as e:
        e.show()
    except MusicbotError as e:
        MusicbotObject.err(e)
    except (
        mutagen.MutagenError,
        spotipy.client.SpotifyException,
        requests.exceptions.ConnectionError,
        edgedb.errors.AuthenticationError
    ) as e:
        logger.error(e)
        if MusicbotObject.config and MusicbotObject.config.debug:
            logger.exception(e)
    finally:
        version_check.print()


if __name__ == '__main__':
    main()
