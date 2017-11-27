# -*- coding: utf-8 -*-
import click
import yaml
from lib import options, filter


@click.group(invoke_without_command=True)
@click.pass_context
@options.add_options(options.filters)
@click.argument('path', type=click.File('w'), default='-')
def cli(ctx, path, **kwargs):
    '''Filter creation'''
    mf = filter.Filter(**kwargs)
    yaml.dump(mf, path, default_flow_style=False)
