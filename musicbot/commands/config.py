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


@cli.command()
def logging():
    '''Show loggers tree'''
    printout()
