'''Musicbot CLI'''
import logging

import click
from click_skeleton import skeleton, add_options
from musicbot.global_options import options
import musicbot.commands

PROG_NAME = "musicbot"
__version__ = "0.7.5"
logger = logging.getLogger(PROG_NAME)


@skeleton(name=PROG_NAME, version=__version__, auto_envvar_prefix='MB')
@click.pass_context
@add_options(options)
def main_cli(ctx, **kwargs):
    """Music swiss knife, new gen."""
    from musicbot.config import config as config_obj
    config_obj.set(**kwargs)


main_cli.add_groups_from_package(musicbot.commands)
