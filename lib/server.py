# -*- coding: utf-8 -*-
import os
import time
from sanic_openapi import swagger_blueprint, openapi_blueprint
from .lib import bytesToHuman, secondsToHuman
from .helpers import timeit
from .database import DbContext
from .web.helpers import env, template, basicauth
from .web.api import api_v1
from .web.collection import collection
from .web.app import app


def basename(path):
    return os.path.basename(path)


def get_flashed_messages():
    return ()


def download_title(m):
    return m['artist'] + ' - ' + m['album'] + ' - ' + basename(m['path'])


# app = Sanic(name='musicbot', log_config=None)
app.blueprint(collection)
app.blueprint(api_v1)
app.blueprint(openapi_blueprint)
app.blueprint(swagger_blueprint)
app.config['WTF_CSRF_SECRET_KEY'] = 'top secret!'
app.config['DB'] = DbContext()
env.globals['get_flashed_messages'] = get_flashed_messages
env.globals['url_for'] = app.url_for
env.globals['bytesToHuman'] = bytesToHuman
env.globals['secondsToHuman'] = secondsToHuman
env.globals['download_title'] = download_title
env.globals['request_time'] = lambda: time.time() - env.globals['request_start_time']
session = {}


@app.middleware('request')
@basicauth
@timeit
async def global_middleware(request):
    env.globals['request_start_time'] = time.time()
    request['session'] = session


@app.route("/")
async def get_root(request):
    return await template('index.html')
