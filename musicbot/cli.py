#!/usr/bin/env python3
import logging
import click
import requests
import spotipy
from click.formatting import HelpFormatter
from click_help_colors import version_option
from mutagen import MutagenError
from attrdict import AttrDict
from musicbot import lib, config, exceptions, backtrace
from musicbot import __version__
from musicbot.click_helpers import AdvancedGroup, add_options, completion
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
HelpFormatter.write_dl.__defaults__ = (50, 2)
backtrace.hook(reverse=False, align=True, strip_path=False, enable_on_envvar_only=False, on_tty=False, conservative=False, styles={})
CONTEXT_SETTINGS = {
    'max_content_width': 140,
    'terminal_width': 140,
    'auto_envvar_prefix': 'MB',
    'help_option_names': ['-h', '--help']
}


@click.group(
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

cli._commands['music'] = ['file']
cli._aliases['file'] = 'music'

@cli.command(short_help='Print version')
def version():
    '''Print version

       Equivalent : -V
    '''
    click.echo(f"{click.style(prog_name, fg='yellow')}, version {click.style(__version__, fg='green')}")


def main(**kwargs):
    try:
        return cli.main(prog_name=prog_name, **kwargs)
    except (MutagenError, exceptions.MusicbotError, spotipy.client.SpotifyException, requests.exceptions.ConnectionError) as e:
        if config.config.debug:
            logger.exception(e)
        else:
            raise


if __name__ == '__main__':
    lib.raise_limits()
    main()
