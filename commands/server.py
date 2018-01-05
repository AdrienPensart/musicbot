# -*- coding: utf-8 -*-
import click
import os
import sys
from logging import debug
from lib import helpers, database, collection, lib, server

THIS_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))


def self_restart():
    python = sys.executable
    os.execl(python, python, * sys.argv)


@click.group()
@click.pass_context
@helpers.add_options(database.options)
@click.option('--watcher', envvar='MB_WATCH', help='Watch for file modification', is_flag=True)
@click.option('--autoscan', envvar='MB_SCHEDULER', help='Enable auto scan background job', is_flag=True)
@click.option('--cache', envvar='MB_BROWSER_CACHE', help='Activate browser cache system', is_flag=True)
@click.option('--browser-cache', envvar='MB_BROWSER_CACHE', help='Activate browser cache system', is_flag=True)
def cli(ctx, watcher, autoscan, cache, browser_cache, **kwargs):
    '''API Server'''
    server.app.config['DB'] = collection.Collection(**kwargs)
    server.app.config['CONFIG'] = ctx.obj.config
    server.app.config['WATCHER'] = watcher
    server.app.config['AUTOSCAN'] = autoscan
    server.app.config['CACHE'] = cache
    server.app.config['BROWSER_CACHE'] = browser_cache
    if not watcher:
        return
    debug('Watching for python and html file changes')
    lib.raise_limits()
    from watchdog.observers import Observer
    from watchdog.events import PatternMatchingEventHandler

    class PyWatcherHandler(PatternMatchingEventHandler):
        patterns = []

        def __init__(self):
            self.patterns = ['*.py', '*.html']
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
    lib_folder = THIS_DIR + '/lib'
    debug('Watching lib folder: {}'.format(lib_folder))
    observer.schedule(event_handler, lib_folder, recursive=True)
    commands_folder = THIS_DIR + '/commands'
    debug('Watching commands folder: {}'.format(commands_folder))
    observer.schedule(event_handler, commands_folder, recursive=True)
    observer.start()


@cli.command()
@click.pass_context
@helpers.add_options(server.options)
def start(ctx, host, port, workers, **kwargs):
    '''Start musicbot web API'''
    server.app.run(host=host, port=port, debug=ctx.obj.config.isDebug(), workers=workers)
