import click
from logging_tree import printout
from musicbot.lib import helpers
from musicbot.lib.config import config


@click.group(cls=helpers.GroupWithHelp)
def cli():
    '''Config management'''


@cli.command()
def show():
    '''Print default config'''
    print(config)


@cli.command()
def logging():
    '''Show loggers tree'''
    printout()
