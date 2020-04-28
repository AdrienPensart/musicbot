#!/usr/bin/env python3
import sys
import os
import logging
import click
import requests
import spotipy
import click_completion
import click_completion.core
from click.formatting import HelpFormatter
from attrdict import AttrDict
from musicbot import lib, helpers, config, exceptions, backtrace
from musicbot import __version__
from musicbot.commands.completion import cli as completion_cli
from musicbot.commands.config import cli as config_cli
from musicbot.commands.folder import cli as folder_cli
from musicbot.commands.local import cli as local_cli
from musicbot.commands.music import cli as music_cli
from musicbot.commands.spotify import cli as spotify_cli
from musicbot.commands.user import cli as user_cli
from musicbot.commands.youtube import cli as youtube_cli

# little hacky but prevent click from rewraping
HelpFormatter.write_dl.__defaults__ = (50, 2)
backtrace.hook(reverse=False, align=True, strip_path=False, enable_on_envvar_only=False, on_tty=False, conservative=False, styles={})
bin_folder = os.path.dirname(__file__)
commands_folder = 'commands'
plugin_folder = os.path.join(bin_folder, commands_folder)
CONTEXT_SETTINGS = {'max_content_width': 140, 'terminal_width': 140, 'auto_envvar_prefix': 'MB', 'help_option_names': ['-h', '--help']}
logger = logging.getLogger('musicbot')


def custom_startswith(string, incomplete):
    """A custom completion matching that supports case insensitive matching"""
    if os.environ.get('_CLICK_COMPLETION_COMMAND_CASE_INSENSITIVE_COMPLETE'):
        string = string.lower()
        incomplete = incomplete.lower()
    return string.startswith(incomplete)


click_completion.core.startswith = custom_startswith
click_completion.init()

prog_name = "musicbot"


@click.group(cls=helpers.GroupWithHelp, context_settings=CONTEXT_SETTINGS, invoke_without_command=True)
@click.version_option(__version__, "--version", "-V", prog_name=prog_name)
@helpers.add_options(config.options)
@click.pass_context
def cli(ctx, **kwargs):
    """Music swiss knife, new gen."""
    ctx.obj = AttrDict
    ctx.obj.folder = bin_folder
    config.config.set(**kwargs)
    ctx.obj.config = config.config


cli.add_command(config_cli, 'config')
cli.add_command(folder_cli, 'folder')
cli.add_command(local_cli, 'local')
cli.add_command(music_cli, 'music')
cli.add_command(spotify_cli, 'spotify')
cli.add_command(youtube_cli, 'youtube')
cli.add_command(user_cli, 'user')
cli.add_command(completion_cli, 'completion')


@cli.command(short_help='Print version')
def version():
    '''Print version

       Equivalent : -V
    '''
    print(f"{prog_name}, version {__version__}")


def main(**kwargs):
    try:
        return cli.main(prog_name=prog_name, **kwargs)
    except (exceptions.MusicbotError, spotipy.client.SpotifyException, requests.exceptions.ConnectionError) as e:
        logger.error(e)
        sys.exit(1)


if __name__ == '__main__':
    lib.raise_limits()
    main()
