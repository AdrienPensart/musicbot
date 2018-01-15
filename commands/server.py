# -*- coding: utf-8 -*-
import click
import os
import sys
from logging import debug
from lib import helpers, database, lib, server
from lib.config import config
from lib.web import config as webconfig

THIS_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))


def self_restart():
    python = sys.executable
    os.execl(python, python, * sys.argv)


@click.group()
@click.pass_context
@helpers.add_options(database.options)
@helpers.add_options(webconfig.options)
def cli(ctx, **kwargs):
    '''API Server'''
    server.app.config.DB.set(**kwargs)
    webconfig.webconfig.set(**kwargs)
    if not webconfig.webconfig.watcher:
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
def start(ctx, http_host, http_port, http_workers, http_user, http_password, **kwargs):
    '''Start musicbot web API'''
    server.app.config.HTTP_USER = http_user
    server.app.config.HTTP_PASSWORD = http_password
    server.app.run(host=http_host, port=http_port, debug=config.isDebug(), workers=http_workers)
