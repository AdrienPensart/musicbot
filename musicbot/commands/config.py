import click
from logging_tree import printout
from musicbot import helpers
from musicbot.config import config


@click.group(hidden=True, cls=helpers.GroupWithHelp)
def cli():
    '''Config management'''


@cli.command()
def show():
    '''Print default config'''
    print(config)


@cli.command('print')
def _print():
    for each_section in config.configfile.sections():
        print(f"[{each_section}]")
        for (each_key, each_val) in config.configfile.items(each_section):
            print(f"    {each_key} = {each_val}")
        print()



@cli.command()
def logging():
    '''Show loggers tree'''
    printout()
