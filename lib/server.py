import time
import os
import click
import logging
from .web import helpers as webhelpers
from . import lib

from aiocache import caches
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sanic_openapi import swagger_blueprint, openapi_blueprint
from . import helpers
from .config import config
from .web.api import api_v1
from .web.collection import collection
from .web.app import app, db
from .web.config import webconfig
# from .web.limiter import limiter

logger = logging.getLogger(__name__)

config.set()

MB_HTTP_USER = 'MB_HTTP_USER'
MB_HTTP_SERVER = 'MB_HTTP_SERVER'
MB_HTTP_PW = 'MB_HTTP_PASSWORD'
MB_HTTP_HOST = 'MB_HTTP_HOST'
MB_HTTP_PORT = 'MB_HTTP_PORT'
MB_HTTP_WORKERS = 'MB_HTTP_WORKERS'

DEFAULT_HTTP_USER = 'musicbot'
DEFAULT_HTTP_SERVER = 'musicbot.ovh'
DEFAULT_HTTP_PASSWORD = helpers.random_password(size=10)
DEFAULT_HTTP_HOST = '127.0.0.1'
DEFAULT_HTTP_PORT = 8000
DEFAULT_HTTP_WORKERS = 1

options = [
    click.option('--http-host', envvar=MB_HTTP_HOST, help='Host interface to listen on', default=DEFAULT_HTTP_HOST, show_default=True),
    click.option('--http-server', envvar=MB_HTTP_SERVER, help='Server name to use in links', default=DEFAULT_HTTP_SERVER, show_default=True),
    click.option('--http-port', envvar=MB_HTTP_PORT, help='HTTP port to listen on', default=DEFAULT_HTTP_PORT, show_default=True),
    click.option('--http-workers', envvar=MB_HTTP_WORKERS, help='Number of HTTP workers (not tested)', default=DEFAULT_HTTP_WORKERS, show_default=True),
    click.option('--http-user', envvar=MB_HTTP_USER, help='HTTP Basic auth user', default=DEFAULT_HTTP_USER, show_default=True),
    click.option('--http-password', envvar=MB_HTTP_PW, help='HTTP Basic auth password', default=DEFAULT_HTTP_PASSWORD, show_default=False),
]


def server():
    if webconfig.no_auth:
        return app.config.HTTP_SERVER
    return app.config.HTTP_USER + ':' + app.config.HTTP_PASSWORD + '@' + app.config.HTTP_SERVER


app.blueprint(collection)
app.blueprint(api_v1)
app.blueprint(openapi_blueprint)
app.blueprint(swagger_blueprint)
webhelpers.env.globals['get_flashed_messages'] = webhelpers.get_flashed_messages
webhelpers.env.globals['url_for'] = app.url_for
webhelpers.env.globals['server'] = server
webhelpers.env.globals['bytes_to_human'] = lib.bytes_to_human
webhelpers.env.globals['seconds_to_human'] = lib.seconds_to_human
webhelpers.env.globals['download_title'] = webhelpers.download_title
webhelpers.env.globals['request_time'] = lambda: lib.seconds_to_human(time.time() - webhelpers.env.globals['request_start_time'])
session = {}
app.config.HTTP_SERVER = DEFAULT_HTTP_SERVER
app.config.HTTP_USER = DEFAULT_HTTP_USER
app.config.HTTP_PASSWORD = DEFAULT_HTTP_PASSWORD
app.config.WTF_CSRF_SECRET_KEY = helpers.random_password(size=12)
app.config.SCHEDULER = None
app.config.LISTENER = None
app.config.CONCURRENCY = 1
app.config.CRAWL = False
app.config.CONFIG = config
app.config.API_VERSION = '1.0.0'
app.config.API_TITLE = 'Musicbot API'
app.config.API_DESCRIPTION = 'Musicbot API'
app.config.API_TERMS_OF_SERVICE = 'Use with caution!'
app.config.API_PRODUCES_CONTENT_TYPES = ['application/json']
app.config.API_CONTACT_EMAIL = 'crunchengine@gmail.com'


# CLOSE DB GRACEFULLY
@app.listener('after_server_stop')
async def close_db(app, loop):
    await db.close()


# AUTHENTICATION
@app.listener('before_server_start')
def init_authentication(app, loop):
    if webconfig.no_auth:
        logger.debug('Authentication disabled')
    else:
        logger.debug('Authentication enabled')
        user = os.getenv('MB_HTTP_USER', app.config.HTTP_USER)
        password = os.getenv('MB_HTTP_PASSWORD', app.config.HTTP_PASSWORD)
        webhelpers.env.globals['auth'] = {'user': user, 'password': password}


# CACHE INVALIDATION
def invalidate_cache(connection, pid, channel, payload):
    logger.debug('Received notification: %s %s %s', pid, channel, payload)
    cache = caches.get('default')
    app.loop.create_task(cache.delete(payload))


@app.listener('before_server_start')
async def init_cache_invalidator(app, loop):
    if webconfig.server_cache:
        logger.debug('Cache invalidator activated')
        app.config.LISTENER = await (await db.pool).acquire()
        await app.config.LISTENER.add_listener('cache_invalidator', invalidate_cache)
    else:
        logger.debug('Cache invalidator disabled')


# FILE WATCHER
@app.listener('before_server_start')
def start_watcher(app, loop):
    if webconfig.watcher:
        logger.debug('File watcher enabled')
        app.config.watcher_task = loop.create_task(helpers.watcher(db))
    else:
        logger.debug('File watcher disabled')


@app.listener('before_server_stop')
def stop_watcher(app, loop):
    if webconfig.watcher:
        app.config.watcher_task.cancel()


# APS SCHEDULER
@app.listener('before_server_start')
def start_scheduler(app, loop):
    if webconfig.autoscan:
        logger.debug('Autoscan enabled')
        app.config.SCHEDULER = AsyncIOScheduler({'event_loop': loop})
        app.config.SCHEDULER.add_job(helpers.refresh_db, 'interval', [db], minutes=15)
        app.config.SCHEDULER.add_job(helpers.fullscan, 'cron', [db], hour=3)
        app.config.SCHEDULER.add_job(helpers.crawl_musics, 'cron', [db], hour=4)
        app.config.SCHEDULER.add_job(helpers.crawl_albums, 'cron', [db], hour=5)
        app.config.SCHEDULER.start()
    else:
        logger.debug('Autoscan disabled')


@app.listener('before_server_stop')
def stop_scheduler(app, loop):
    if webconfig.autoscan:
        app.config.SCHEDULER.shutdown(wait=False)


# REQUEST TIMER
@app.middleware('request')
def before(request):
    webhelpers.env.globals['request_start_time'] = time.time()
    request['session'] = session


# BROWSER CACHE
@app.middleware('response')
def after(request, response):
    if webconfig.client_cache:
        logger.debug('Browser cache enabled')
    else:
        logger.info('Browser cache disabled')
        if response is not None:
            response.headers['Last-Modified'] = datetime.now()
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '-1'


@app.route("/")
@webhelpers.basicauth
async def get_root(request):
    return await webhelpers.template('index.html')

app.static('/static', './lib/web/templates/static')
