#!/usr/bin/env python3
"""Main module, import commands and start CLI"""
import logging
import os
from typing import Any

import acoustid  # type: ignore
import click
import gel
import mutagen
import requests
import spotipy  # type: ignore
from beartype import beartype
from click_skeleton import backtrace, doc, helpers, skeleton, version_checker

import musicbot
import musicbot.commands
from musicbot import Config, MusicbotObject, version
from musicbot.cli.config import config_options
from musicbot.cli.options import dry_option

PROG_NAME: str = "musicbot"
logger = logging.getLogger(__name__)


@skeleton(name=PROG_NAME, version=version.__version__, auto_envvar_prefix="MB", groups_package=musicbot.commands)
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

    if not helpers.raise_limits():
        MusicbotObject.err("unable to raise ulimit")

    ctx.color = MusicbotObject.config.color


@cli.command(short_help="Starts interpreter")
@beartype
def console() -> None:
    """Starts an embedded ipython interpreter"""
    import IPython

    user_ns = dict(
        musicbot=musicbot,
        MusicbotObject=MusicbotObject,
    )
    IPython.start_ipython(argv=["--no-confirm-exit"], user_ns=user_ns)


@cli.command(short_help="Generates a README.rst", aliases=["doc"])
@click.pass_context
@click.option("--output", help="README output format", type=click.Choice(["rst", "markdown"]), default="rst", show_default=True)
@beartype
def readme(ctx: click.Context, output: str) -> None:
    """Generates a complete readme"""
    doc.readme(cli, ctx.obj.prog_name, ctx.obj.context_settings, output)


def main() -> None:
    check_version = helpers.str2bool(os.environ.get("MB_CHECK_VERSION", MusicbotObject.is_prod()))
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
    except spotipy.oauth2.SpotifyOauthError as error:
        MusicbotObject.err("Authentication error", error=error)
    except (mutagen.MutagenError, spotipy.client.SpotifyException, requests.exceptions.ConnectionError, gel.errors.AuthenticationError, acoustid.WebServiceError) as error:
        MusicbotObject.err("Internal Error", error=error)
    finally:
        version_check.print()


if __name__ == "__main__":
    main()
