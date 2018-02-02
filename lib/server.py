# -*- coding: utf-8 -*-
import time
import os
import click
from aiocache import caches
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sanic_openapi import swagger_blueprint, openapi_blueprint
from .lib import bytesToHuman, secondsToHuman
from .helpers import refresh_db, crawl_musics, crawl_albums, watcher, fullscan
from .config import config
from .web.helpers import env, template, get_flashed_messages, download_title, server
from .web.api import api_v1
from .web.collection import collection
from .web.app import app
from .web.config import webconfig
from logging import debug, info
# from .web.limiter import limiter
# from logging_tree import printout
# printout()

DEFAULT_HTTP_USER = 'musicbot'
DEFAULT_HTTP_PASSWORD = 'musicbot'
DEFAULT_HTTP_HOST = '127.0.0.1'
DEFAULT_HTTP_PORT = 8000
DEFAULT_HTTP_WORKERS = 1

options = [
    click.option('--http-host', envvar='MB_HTTP_HOST', help='Host interface to listen on', default=DEFAULT_HTTP_HOST),
    click.option('--http-port', envvar='MB_HTTP_PORT', help='HTTP port to listen on', default=DEFAULT_HTTP_PORT),
    click.option('--http-workers', envvar='MB_HTTP_WORKERS', help='Number of HTTP workers (not tested)', default=DEFAULT_HTTP_WORKERS),
    click.option('--http-user', envvar='MB_HTTP_USER', help='HTTP Basic auth user', default=DEFAULT_HTTP_USER),
    click.option('--http-password', envvar='MB_HTTP_PASSWORD', help='HTTP Basic auth password', default=DEFAULT_HTTP_PASSWORD),
]

app.blueprint(collection)
app.blueprint(api_v1)
app.blueprint(openapi_blueprint)
app.blueprint(swagger_blueprint)
env.globals['server_name'] = 'api.musicbot.ovh'
env.globals['get_flashed_messages'] = get_flashed_messages
env.globals['url_for'] = app.url_for
env.globals['server'] = server
env.globals['bytesToHuman'] = bytesToHuman
env.globals['secondsToHuman'] = secondsToHuman
env.globals['download_title'] = download_title
env.globals['request_time'] = lambda: secondsToHuman(time.time() - env.globals['request_start_time'])
session = {}

app.config.HTTP_USER = DEFAULT_HTTP_USER
app.config.HTTP_PASSWORD = DEFAULT_HTTP_PASSWORD
app.config.WTF_CSRF_SECRET_KEY = 'top secret!'
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


# AUTHENTICATION
@app.listener('before_server_start')
async def init_authentication(app, loop):
    user = os.getenv('MB_HTTP_USER', app.config.HTTP_USER)
    password = os.getenv('MB_HTTP_PASSWORD', app.config.HTTP_PASSWORD)
    env.globals['auth'] = {'user': user, 'password': password}


# CACHE INVALIDATION
def invalidate_cache(connection, pid, channel, payload):
    debug('Received notification: {} {} {}'.format(pid, channel, payload))
    cache = caches.get('default')
    app.loop.create_task(cache.delete(payload))


@app.listener('before_server_start')
async def init_cache_invalidator(app, loop):
    print(webconfig)
    if webconfig.server_cache:
        debug('Cache invalidator activated')
        app.config.LISTENER = await (await app.config.DB.pool).acquire()
        await app.config.LISTENER.add_listener('cache_invalidator', invalidate_cache)
    else:
        debug('Cache invalidator disabled')


# FILE WATCHER
@app.listener('before_server_start')
async def start_watcher(app, loop):
    if webconfig.watcher:
        debug('File watcher enabled')
        app.config.watcher_task = loop.create_task(watcher(app.config.DB))
    else:
        debug('File watcher disabled')


@app.listener('before_server_stop')
async def stop_watcher(app, loop):
    if webconfig.watcher:
        app.config.watcher_task.cancel()


# APS SCHEDULER
@app.listener('before_server_start')
async def start_scheduler(app, loop):
    if webconfig.autoscan:
        debug('Autoscan enabled')
        app.config.SCHEDULER = AsyncIOScheduler({'event_loop': loop})
        app.config.SCHEDULER.add_job(refresh_db, 'interval', [app.config.DB], hours=1)
        app.config.SCHEDULER.add_job(fullscan, 'cron', [app.config.DB], hour=3)
        app.config.SCHEDULER.add_job(crawl_musics, 'cron', [app.config.DB], hour=4)
        app.config.SCHEDULER.add_job(crawl_albums, 'cron', [app.config.DB], hour=5)
        app.config.SCHEDULER.start()
    else:
        debug('Autoscan disabled')


@app.listener('before_server_stop')
async def stop_scheduler(app, loop):
    if webconfig.autoscan:
        app.config.SCHEDULER.shutdown(wait=False)


# REQUEST TIMER
@app.middleware('request')
async def before(request):
    env.globals['request_start_time'] = time.time()
    request['session'] = session


# BROWSER CACHE
@app.middleware('response')
async def after(request, response):
    if webconfig.client_cache:
        debug('Browser cache enabled')
    else:
        info('Browser cache disabled')
        response.headers['Last-Modified'] = datetime.now()
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'


@app.route("/")
async def get_root(request):
    return await template('index.html')

app.static('/static', './lib/web/templates/static')
