# -*- coding: utf-8 -*-
import click
from lib import helpers

@click.group(invoke_without_command=False)
@helpers.pass_context
def cli(ctx):
    click.echo('cli')

@cli.command()
@helpers.pass_context
def create():
    click.echo('create')

@cli.command()
@herlpers.pass_context
def drop():
    click.echo('drop')

@cli.command()
@helpers.pass_context
def clear():
    click.echo('clear')

@cli.command()
@helpers.pass_context
def clean():
    click.echo('clean')
