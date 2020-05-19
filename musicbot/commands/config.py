import logging
import click
from logging_tree import printout
from musicbot import helpers
from musicbot.config import config

logger = logging.getLogger('musicbot')


@click.group(hidden=True, help='Config management', cls=helpers.GroupWithHelp)
def cli():
    pass


@cli.command(help='Print global config')
def show():
    print(config)


@cli.command('print', help='Print config file')
def _print():
    for each_section in config.configfile.sections():
        print(f"[{each_section}]")
        for (each_key, each_val) in config.configfile.items(each_section):
            print(f"    {each_key} = {each_val}")
        print()



@cli.command('logging', help='Print logging config')
def _logging():
    printout()
