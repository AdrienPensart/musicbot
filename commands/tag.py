# -*- coding: utf-8 -*-
import click
from lib import helpers
from logging import debug, info, warning, error, critical

@click.group(invoke_without_command=True)
@helpers.add_options(helpers.filter_options)
@helpers.pass_context
def cli(ctx, **kwargs):
    debug(kwargs)
    click.echo('cli')

@cli.command()
@helpers.pass_context
def show(ctx, **kwargs):
    debug(kwargs)
    click.echo('show')

@cli.command()
@helpers.pass_context
def add(ctx, **kwargs):
    debug(kwargs)
    click.echo('add')

@cli.command()
@helpers.pass_context
def delete(ctx, *kwargs):
    debug(kwargs)
    click.echo('delete')
