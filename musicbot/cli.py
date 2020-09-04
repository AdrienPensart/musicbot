#!/usr/bin/env python3
import logging
from packaging import version

import click
import requests
import spotipy

from mutagen import MutagenError
from attrdict import AttrDict

from click_help_colors import version_option
from click_skeleton import AdvancedGroup, add_options, backtrace
from click_skeleton.completion import completion

from musicbot import config, exceptions, __version__
from musicbot.music.helpers import raise_limits
from musicbot.commands.config import cli as config_cli
from musicbot.commands.folder import cli as folder_cli
from musicbot.commands.local import cli as local_cli
from musicbot.commands.music import cli as music_cli
from musicbot.commands.spotify import cli as spotify_cli
from musicbot.commands.user import cli as user_cli
from musicbot.commands.youtube import cli as youtube_cli

prog_name = "musicbot"
logger = logging.getLogger('musicbot')
# little hacky but prevent click from rewraping
click.formatting.HelpFormatter.write_dl.__defaults__ = (50, 2)

backtrace.hook(reverse=False, align=True, strip_path=False, enable_on_envvar_only=False, on_tty=False, conservative=False, styles={})
CONTEXT_SETTINGS = {
    'max_content_width': 140,
    'terminal_width': 140,
    'auto_envvar_prefix': 'MB',
    'help_option_names': ['-h', '--help']
}


@click.group(
    prog_name,
    cls=AdvancedGroup,
    context_settings=CONTEXT_SETTINGS,
)
@version_option(
    __version__,
    "--version", "-V",
    version_color='green',
    prog_name=prog_name,
    prog_name_color='yellow',
)
@add_options(config.options)
@click.pass_context
def cli(ctx, **kwargs):
    """Music swiss knife, new gen."""
    ctx.obj = AttrDict
    config.config.set(**kwargs)
    ctx.obj.config = config.config


cli.add_command(config_cli, 'config')
cli.add_command(folder_cli, 'folder')
cli.add_command(local_cli, 'local')
cli.add_command(music_cli, 'music')
cli.add_command(spotify_cli, 'spotify')
cli.add_command(youtube_cli, 'youtube')
cli.add_command(user_cli, 'user')
cli.add_command(completion, 'completion')

# hacky aliases
cli._commands['music'] = ['file']
cli._aliases['file'] = 'music'


@cli.command('version', short_help='Print version')
def _version():
    '''Print version

       Equivalent : -V
    '''
    click.echo(f"{click.style(prog_name, fg='yellow')}, version {click.style(__version__, fg='green')}")
    response = requests.get(f'https://pypi.org/pypi/{prog_name}/json')
    latest_version = response.json()['info']['version']
    if version.parse(latest_version) > version.parse(__version__):
        logger.warning(f"A new {prog_name} version is available on PyPI : {latest_version}")


def main(**kwargs):
    try:
        return cli.main(prog_name=prog_name, **kwargs)
    except (MutagenError, exceptions.MusicbotError, spotipy.client.SpotifyException, requests.exceptions.ConnectionError) as e:
        if config.config.debug:
            logger.exception(e)
        else:
            raise


if __name__ == '__main__':
    raise_limits()
    main()
