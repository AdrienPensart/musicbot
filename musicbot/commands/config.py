import logging

import click
from beartype import beartype
from click_skeleton import AdvancedGroup
from logging_tree import printout  # type: ignore

from musicbot.object import MusicbotObject

logger = logging.getLogger('musicbot')


@click.group('config', hidden=True, help='Config management', cls=AdvancedGroup)
@beartype
def cli() -> None:
    pass


@cli.command(help='Print global config')
@beartype
def show() -> None:
    print(MusicbotObject.config)


@cli.command(help='Write in global config')
@click.argument('section')
@click.argument('key')
@click.argument('value')
@beartype
def write(section: str, key: str, value: str) -> None:
    if not MusicbotObject.config.configfile.has_section(section):
        MusicbotObject.config.configfile.add_section(section)
    MusicbotObject.config.configfile[section][key] = value
    MusicbotObject.config.write()


@cli.command('print', help='Print config file')
@beartype
def _print() -> None:
    for each_section in MusicbotObject.config.configfile.sections():
        print(f"[{each_section}]")
        for (each_key, each_val) in MusicbotObject.config.configfile.items(each_section):
            print(f"    {each_key} = {each_val}")
        print()


@cli.command('logging', help='Print logging config')
@beartype
def _logging() -> None:
    printout()
