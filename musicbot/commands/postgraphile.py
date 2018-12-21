import logging
import click
from musicbot import helpers
from musicbot.backend import database, postgraphile
from musicbot.backend.postgraphile import public_options, private_options

logger = logging.getLogger(__name__)


@click.group(cls=helpers.GroupWithHelp)
def cli():
    '''Postgraphile management'''


@cli.command()
@helpers.add_options(database.db_option + public_options)
def public(db, jwt_secret, graphql_public_interface, graphql_public_port, **kwargs):
    '''Start public backend'''
    pql = postgraphile.Postgraphile.public(db=db, jwt_secret=jwt_secret, interface=graphql_public_interface, port=graphql_public_port)
    pql.run(**kwargs)


@cli.command()
@helpers.add_options(database.db_option + private_options)
def private(db, graphql_private_interface, graphql_private_port, **kwargs):
    '''Start private backend'''
    pql = postgraphile.Postgraphile.private(db=db, interface=graphql_private_interface, port=graphql_private_port)
    pql.run(**kwargs)
