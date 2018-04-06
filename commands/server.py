# -*- coding: utf-8 -*-
import click
import os
import sys
from logging import debug
from lib import helpers, database, lib, server
from lib.config import config
from lib.web import config as webconfig

@click.group()
@click.pass_context
@helpers.add_options(database.options)
@helpers.add_options(webconfig.options)
def cli(ctx, **kwargs):
    '''API Server'''
    server.app.config.DB.set(**kwargs)
    webconfig.webconfig.set(**kwargs)
    if not webconfig.webconfig.dev:
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
            self.restart()

        def on_created(self, event):
            debug('Created: {} {}'.format(event.src_path, event.event_type))
            self.restart()

        def on_deleted(self, event):
            debug('Deleted: {} {}'.format(event.src_path, event.event_type))
            self.restart()

        def on_moved(self, event):
            debug('Moved: {} {}'.format(event.src_path, event.event_type))
            self.restart()

        def restart(self):
            python = sys.executable
            os.execl(python, python, * sys.argv)


    event_handler = PyWatcherHandler()
    observer = Observer()

    for f in ['lib', 'commands']:
        fpath = os.path.join(ctx.obj.folder, f)
        debug('Watching internal folder: {}'.format(fpath))
        observer.schedule(event_handler, fpath, recursive=True)
    observer.start()


@cli.command()
@click.pass_context
@helpers.add_options(server.options)
def start(ctx, http_host, http_server, http_port, http_workers, http_user, http_password, **kwargs):
    '''Start musicbot web API'''
    server.app.config.HTTP_SERVER = http_server
    server.app.config.HTTP_USER = http_user
    server.app.config.HTTP_PASSWORD = http_password
    server.app.run(host=http_host, port=http_port, debug=config.isDebug(), workers=http_workers)
