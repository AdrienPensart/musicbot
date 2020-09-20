#!/usr/bin/env python3
# pytype: disable=attribute-error
import logging
import click
import requests
import spotipy  # type: ignore
import mutagen  # type: ignore
import attrdict  # type: ignore

from click_help_colors import version_option  # type: ignore
from click_skeleton import AdvancedGroup, add_options, backtrace, version_checker
from click_skeleton.completion import completion
from click_skeleton.helpers import raise_limits

from musicbot import config, exceptions, __version__
from musicbot.config import config as config_obj
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
click.formatting.HelpFormatter.write_dl.__defaults__ = (50, 2)  # type: ignore

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
    ctx.obj = attrdict.AttrDict
    config_obj.set(**kwargs)
    ctx.obj.config = config_obj


cli.add_command(config_cli, 'config')
cli.add_command(folder_cli, 'folder')
cli.add_command(local_cli, 'local')
cli.add_command(music_cli, 'music')
cli.add_command(spotify_cli, 'spotify')
cli.add_command(youtube_cli, 'youtube')
cli.add_command(user_cli, 'user')
cli.add_command(completion, 'completion')

# hacky aliases
cli._commands['music'] = ['file']  # type: ignore
cli._aliases['file'] = 'music'  # type: ignore


@cli.command('version', short_help='Print version')
def _version():
    '''Print version

       Equivalent : -V
    '''
    click.echo(f"{click.style(prog_name, fg='yellow')}, version {click.style(__version__, fg='green')}")


def main(**kwargs):
    version_check = version_checker.VersionCheckerThread(
        prog_name=prog_name,
        current_version=__version__,
        autostart=config_obj.check_version,
    )
    try:
        return cli.main(prog_name=prog_name, **kwargs)
    except (mutagen.MutagenError, exceptions.MusicbotError, spotipy.client.SpotifyException, requests.exceptions.ConnectionError) as e:
        if config_obj.debug:
            logger.exception(e)
        else:
            raise
    finally:
        if version_check.is_alive():
            version_check.join()
            if version_check.new_version_warning:
                click.echo(version_check.new_version_warning, err=True)


if __name__ == '__main__':
    raise_limits()
    main()
