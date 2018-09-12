import click
import os
import logging
from lib import helpers, database, server
from lib.config import config
from lib.lib import raise_limits, restart
from lib.web import config as webconfig

logger = logging.getLogger(__name__)


@click.group(cls=helpers.GroupWithHelp)
@helpers.add_options(database.options)
def cli(**kwargs):
    '''API Server'''
    server.app.config.DB.set(**kwargs)


@cli.command()
@click.pass_context
@helpers.add_options(server.options)
@helpers.add_options(webconfig.options)
def start(ctx, http_host, http_server, http_port, http_workers, http_user, http_password, **kwargs):
    '''Start musicbot web API'''
    webconfig.webconfig.set(**kwargs)
    if webconfig.webconfig.dev:
        logger.debug('Watching for python and html file changes')
        raise_limits()
        from watchdog.observers import Observer
        from watchdog.events import PatternMatchingEventHandler

        class PyWatcherHandler(PatternMatchingEventHandler):
            patterns = []

            def __init__(self):
                self.patterns = ['*.py', '*.html']
                super().__init__()

            @staticmethod
            def on_modified(event):
                logger.debug('Modified: %s %s', event.src_path, event.event_type)
                restart()

            @staticmethod
            def on_created(event):
                logger.debug('Created: %s %s', event.src_path, event.event_type)
                restart()

            @staticmethod
            def on_deleted(event):
                logger.debug('Deleted: %s %s', event.src_path, event.event_type)
                restart()

            @staticmethod
            def on_moved(event):
                logger.debug('Moved: %s %s', event.src_path, event.event_type)
                restart()

        event_handler = PyWatcherHandler()
        observer = Observer()

        for f in ['lib', 'commands']:
            fpath = os.path.join(ctx.obj.folder, f)
            logger.debug('Watching internal folder: %s', fpath)
            observer.schedule(event_handler, fpath, recursive=True)
        observer.start()

    server.app.config.HTTP_SERVER = http_server
    server.app.config.HTTP_USER = http_user
    server.app.config.HTTP_PASSWORD = http_password
    server.app.run(host=http_host, port=http_port, debug=config.debug, workers=http_workers)
