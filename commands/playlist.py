# -*- coding: utf-8 -*-
import click
from lib import helpers
from logging import debug, info, warning, error, critical
import inspect
myself = lambda: inspect.stack()[1][3]

@click.group(invoke_without_command=True)
@helpers.add_options(helpers.filter_options)
@helpers.pass_context
def cli(ctx, **kwargs):
    debug(kwargs)

@cli.command()
@helpers.pass_context
def bests(ctx, **kwargs):
    debug(myself())
    debug(kwargs)

