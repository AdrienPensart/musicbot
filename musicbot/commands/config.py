import logging
import click
from logging_tree import printout  # type: ignore
from click_skeleton import AdvancedGroup
from musicbot.cli import main_cli
from musicbot.config import config as config_obj

logger = logging.getLogger('musicbot')


@main_cli.group('config', hidden=True, help='Config management', cls=AdvancedGroup)
def config_cli():
    pass


@config_cli.command(help='Print global config')
def show():
    print(config_obj)


@config_cli.command(help='Write in global config')
@click.argument('section')
@click.argument('key')
@click.argument('value')
def write(section, key, value):
    if not config_obj.configfile.has_section(section):
        config_obj.configfile.add_section(section)
    config_obj.configfile[section][key] = value
    config_obj.write()


@config_cli.command('print', help='Print config file')
def _print():
    for each_section in config_obj.configfile.sections():
        print(f"[{each_section}]")
        for (each_key, each_val) in config_obj.configfile.items(each_section):
            print(f"    {each_key} = {each_val}")
        print()


@config_cli.command('logging', help='Print logging config')
def _logging():
    printout()
