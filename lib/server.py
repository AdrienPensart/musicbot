# -*- coding: utf-8 -*-
import time
from sanic_openapi import swagger_blueprint, openapi_blueprint
from .lib import bytesToHuman, secondsToHuman
from .helpers import timeit
from .database import DbContext
from .web.helpers import env, template, basicauth, get_flashed_messages, download_title, server
from .web.api import api_v1
from .web.collection import collection
from .web.app import app

app.blueprint(collection)
app.blueprint(api_v1)
app.blueprint(openapi_blueprint)
app.blueprint(swagger_blueprint)
app.config['WTF_CSRF_SECRET_KEY'] = 'top secret!'
app.config['DB'] = DbContext()
env.globals['server_name'] = 'api.musicbot.ovh'
env.globals['get_flashed_messages'] = get_flashed_messages
env.globals['url_for'] = app.url_for
env.globals['server'] = server
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
    from logging_tree import printout
    printout()


@app.route("/")
async def get_root(request):
    return await template('index.html')
