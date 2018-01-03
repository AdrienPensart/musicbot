# -*- coding: utf-8 -*-
import time
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sanic_openapi import swagger_blueprint, openapi_blueprint
from .lib import bytesToHuman, secondsToHuman
from .helpers import crawl_musics, crawl_albums, watcher, fullscan
from .config import config
from .collection import Collection
from .web.helpers import env, template, get_flashed_messages, download_title, server
from .web.api import api_v1
from .web.collection import collection
from .web.app import app
# from .web.limiter import limiter
# from logging_tree import printout
# printout()

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

app.config.WTF_CSRF_SECRET_KEY = 'top secret!'
app.config.DB = Collection()
app.config.CONCURRENCY = 1
app.config.CRAWL = False
app.config.CONFIG = config
app.config.API_VERSION = '1.0.0'
app.config.API_TITLE = 'Musicbot API'
app.config.API_DESCRIPTION = 'Musicbot API'
app.config.API_TERMS_OF_SERVICE = 'Use with caution!'
app.config.API_PRODUCES_CONTENT_TYPES = ['application/json']
app.config.API_CONTACT_EMAIL = 'crunchengine@gmail.com'


@app.listener('before_server_start')
async def start_watcher(app, loop):
    app.config.watcher_task = loop.create_task(watcher(app.config.DB))


@app.listener('before_server_stop')
async def stop_watcher(app, loop):
    app.config.watcher_task.cancel()


@app.listener('before_server_start')
async def initialize_scheduler(app, loop):
    scheduler = AsyncIOScheduler({'event_loop': loop})
    scheduler.add_job(fullscan, 'cron', [app.config.DB], hour=3)
    scheduler.add_job(crawl_musics, 'cron', [app.config.DB], hour=4)
    scheduler.add_job(crawl_albums, 'cron', [app.config.DB], hour=5)
    scheduler.start()


@app.middleware('request')
async def before(request):
    env.globals['request_start_time'] = time.time()
    request['session'] = session


@app.middleware('response')
async def after(request, response):
    if 'DEV' in app.config:
        response.headers['Last-Modified'] = datetime.now()
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'


@app.route("/")
async def get_root(request):
    return await template('index.html')

app.static('/static', './lib/web/templates/static')
