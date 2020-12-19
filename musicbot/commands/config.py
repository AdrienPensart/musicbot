import logging
import click
from logging_tree import printout  # type: ignore
from click_skeleton import AdvancedGroup
from musicbot.config import Conf

logger = logging.getLogger('musicbot')


@click.group('config', hidden=True, help='Config management', cls=AdvancedGroup)
def cli():
    pass


@cli.command(help='Print global config')
def show():
    print(Conf.config)


@cli.command(help='Write in global config')
@click.argument('section')
@click.argument('key')
@click.argument('value')
def write(section, key, value):
    if not Conf.config.configfile.has_section(section):
        Conf.config.configfile.add_section(section)
    Conf.config.configfile[section][key] = value
    Conf.config.write()


@cli.command('print', help='Print config file')
def _print():
    for each_section in Conf.config.configfile.sections():
        print(f"[{each_section}]")
        for (each_key, each_val) in Conf.config.configfile.items(each_section):
            print(f"    {each_key} = {each_val}")
        print()


@cli.command('logging', help='Print logging config')
def _logging():
    printout()
