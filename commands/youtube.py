# -*- coding: utf-8 -*-
import click
from lib import helpers

@click.group(invoke_without_command=True)
@helpers.pass_context
def cli(ctx):
    click.echo('cli')

@helpers.command()
def sync():
    click.echo('The subcommand')
