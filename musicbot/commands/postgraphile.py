import click
import os
import logging
from musicbot import helpers
from musicbot.backend import database, postgraphile
from musicbot.backend.postgraphile import public_options, private_options

logger = logging.getLogger(__name__)


@click.group(cls=helpers.GroupWithHelp)
def cli():
    '''Postgraphile management'''


@cli.command()
@helpers.add_options(database.db_option + public_options)
def public(**kwargs):
    '''Start public backend'''
    cmd = postgraphile.public(**kwargs)
    os.system(cmd)


@cli.command()
@helpers.add_options(database.db_option + private_options)
def private(**kwargs):
    '''Start private backend'''
    cmd = postgraphile.private(**kwargs)
    os.system(cmd)
