import logging
import click
from logging_tree import printout
from click_skeleton import AdvancedGroup
from musicbot.config import config

logger = logging.getLogger('musicbot')


@click.group(hidden=True, help='Config management', cls=AdvancedGroup)
def cli():
    pass


@cli.command(help='Print global config')
def show():
    print(config)


@cli.command(help='Write in global config')
@click.argument('section')
@click.argument('key')
@click.argument('value')
def write(section, key, value):
    if not config.configfile.has_section(section):
        config.configfile.add_section(section)
    config.configfile[section][key] = value
    config.write()


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
