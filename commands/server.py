# -*- coding: utf-8 -*-
import click
import os
import sys
from logging import debug
from lib import database, options, lib
from lib.server import app

THIS_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))


def self_restart():
    python = sys.executable
    os.execl(python, python, * sys.argv)


@click.group()
@options.add_options(options.db)
@click.pass_context
def cli(ctx, **kwargs):
    '''API Server'''
    ctx.obj.db = database.DbContext(**kwargs)
    lib.raise_limits()
    from watchdog.observers import Observer
    from watchdog.events import PatternMatchingEventHandler

    class PyWatcherHandler(PatternMatchingEventHandler):
        patterns = ['*.py']

        def __init__(self):
            super().__init__()

        def on_modified(self, event):
            debug('Modified: {} {}'.format(event.src_path, event.event_type))
            self_restart()

        def on_created(self, event):
            debug('Created: {} {}'.format(event.src_path, event.event_type))
            self_restart()

        def on_deleted(self, event):
            debug('Deleted: {} {}'.format(event.src_path, event.event_type))
            self_restart()

        def on_moved(self, event):
            debug('Moved: {} {}'.format(event.src_path, event.event_type))
            self_restart()

    event_handler = PyWatcherHandler()
    observer = Observer()
    observer.schedule(event_handler, THIS_DIR, recursive=True)
    observer.start()


@cli.command()
@click.option('--host', help='Host interface to listen on', default='0.0.0.0')
@click.option('--port', help='Port to listen on', default=8000)
@click.option('--workers', help='Number of workers', default=1)
@click.pass_context
def start(ctx, host, port, workers, **kwargs):
    '''Start musicbot web API'''
    app.config['CTX'] = ctx
    app.run(host=host, port=port, debug=ctx.obj.config.isDebug(), workers=workers)
