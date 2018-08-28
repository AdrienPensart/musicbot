# -*- coding: utf-8 -*-
import click
import os
import sys
import logging
from lib import helpers, database, lib, server
from lib.config import config
from lib.web import config as webconfig
from click_didyoumean import DYMGroup

logger = logging.getLogger(__name__)


@click.group(cls=DYMGroup)
@click.pass_context
@helpers.add_options(database.options + webconfig.options)
def cli(ctx, **kwargs):
    '''API Server'''
    server.app.config.DB.set(**kwargs)
    webconfig.webconfig.set(**kwargs)
    if not webconfig.webconfig.dev:
        return
    logger.debug('Watching for python and html file changes')
    lib.raise_limits()
    from watchdog.observers import Observer
    from watchdog.events import PatternMatchingEventHandler

    class PyWatcherHandler(PatternMatchingEventHandler):
        patterns = []

        def __init__(self):
            self.patterns = ['*.py', '*.html']
            super().__init__()

        def on_modified(self, event):
            logger.debug('Modified: {} {}'.format(event.src_path, event.event_type))
            self.restart()

        def on_created(self, event):
            logger.debug('Created: {} {}'.format(event.src_path, event.event_type))
            self.restart()

        def on_deleted(self, event):
            logger.debug('Deleted: {} {}'.format(event.src_path, event.event_type))
            self.restart()

        def on_moved(self, event):
            logger.debug('Moved: {} {}'.format(event.src_path, event.event_type))
            self.restart()

        def restart(self):
            python = sys.executable
            os.execl(python, python, * sys.argv)

    event_handler = PyWatcherHandler()
    observer = Observer()

    for f in ['lib', 'commands']:
        fpath = os.path.join(ctx.obj.folder, f)
        logger.debug('Watching internal folder: {}'.format(fpath))
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
    server.app.run(host=http_host, port=http_port, debug=config.debug, workers=http_workers)
