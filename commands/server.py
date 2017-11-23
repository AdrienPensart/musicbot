# -*- coding: utf-8 -*-
import click
from lib import database, options
from lib.server import app


def restart_program():
    import sys
    import os
    python = sys.executable
    os.execl(python, python, * sys.argv)


@click.group()
@options.add_options(options.db)
@click.pass_context
def cli(ctx, **kwargs):
    '''API Server'''
    ctx.obj.db = database.DbContext(**kwargs)


@cli.command()
@click.option('--host', help='Host interface to listen on', default='0.0.0.0')
@click.option('--port', help='Port to listen on', default=8000)
@click.option('--workers', help='Number of workers', default=1)
@click.pass_context
def start(ctx, host, port, workers, **kwargs):
    '''Start musicbot web API'''
    app.config['CTX'] = ctx
    app.run(host=host, port=port, debug=ctx.obj.config.isDebug(), workers=workers)
