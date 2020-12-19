'''Musicbot CLI'''
import logging
from typing import Any
from click_skeleton import skeleton, add_options
import musicbot
from musicbot.config import Conf, Config
from musicbot.global_options import options
import musicbot.commands

PROG_NAME = "musicbot"
__version__ = "0.7.5"
logger = logging.getLogger(PROG_NAME)


@skeleton(name=PROG_NAME, version=__version__, auto_envvar_prefix='MB')
@add_options(options)
def main_cli(**kwargs) -> Any:
    """Music swiss knife, new gen."""
    Conf.config = Config(**kwargs)


main_cli.add_groups_from_package(musicbot.commands)
