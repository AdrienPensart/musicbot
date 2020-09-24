'''Musicbot CLI'''
import logging
import click
from click_skeleton import skeleton, add_options
from musicbot.global_options import options

PROG_NAME = "musicbot"
__version__ = "0.7.5"
logger = logging.getLogger(PROG_NAME)


@skeleton(name=PROG_NAME, version=__version__)
@click.pass_context
@add_options(options)
def main_cli(ctx, **kwargs):
    """Music swiss knife, new gen."""
    from musicbot import commands
    from musicbot.config import config as config_obj
    config_obj.set(**kwargs)
    ctx.obj.config = config_obj
    logger.debug(f"Imported commands: {commands.modules}")
