'''Musicbot CLI'''
import logging
import click
from click_skeleton import skeleton, sensible_context_settings, add_options
from musicbot.global_options import options

PROG_NAME = "musicbot"
__version__ = "0.7.3"
CONTEXT_SETTINGS = sensible_context_settings(PROG_NAME, __version__, auto_envvar_prefix='MB')
logger = logging.getLogger(PROG_NAME)


@skeleton(context_settings=CONTEXT_SETTINGS)
@click.pass_context
@add_options(options)
def main_cli(ctx, **kwargs):
    """Music swiss knife, new gen."""
    from musicbot import commands
    from musicbot.config import config as config_obj
    config_obj.set(**kwargs)
    ctx.obj.config = config_obj
    logger.debug(f"Imported commands: {commands.modules}")


@main_cli.command('version', short_help='Print version')
def _version() -> None:
    '''Print version

       Equivalent : -V
    '''
    click.echo(f"{click.style(PROG_NAME, fg='yellow')}, version {click.style(__version__, fg='green')}")
