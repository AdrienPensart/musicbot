# -*- coding: utf-8 -*-
import time
from sanic import response
from sanic_openapi import swagger_blueprint, openapi_blueprint
from .lib import bytesToHuman, secondsToHuman
from .database import DbContext
from .web.helpers import env, template, get_flashed_messages, download_title, server
from .web.api import api_v1
from .web.collection import collection
from .web.app import app
from .web.limiter import limiter
# from logging_tree import printout
# printout()

app.blueprint(collection)
app.blueprint(api_v1)
app.blueprint(openapi_blueprint)
app.blueprint(swagger_blueprint)
app.config.WTF_CSRF_SECRET_KEY = 'top secret!'
app.config.DB = DbContext()
env.globals['server_name'] = 'api.musicbot.ovh'
env.globals['get_flashed_messages'] = get_flashed_messages
env.globals['url_for'] = app.url_for
env.globals['server'] = server
env.globals['bytesToHuman'] = bytesToHuman
env.globals['secondsToHuman'] = secondsToHuman
env.globals['download_title'] = download_title
env.globals['request_time'] = lambda: secondsToHuman(time.time() - env.globals['request_start_time'])
session = {}

app.config.API_VERSION = '1.0.0'
app.config.API_TITLE = 'Musicbot API'
app.config.API_DESCRIPTION = 'Musicbot API'
app.config.API_TERMS_OF_SERVICE = 'Use with caution!'
app.config.API_PRODUCES_CONTENT_TYPES = ['application/json']
app.config.API_CONTACT_EMAIL = 'crunchengine@gmail.com'


@app.middleware('request')
async def global_middleware(request):
    env.globals['request_start_time'] = time.time()
    request['session'] = session


@app.route("/")
async def get_root(request):
    return await template('index.html')


@app.route("/test")
@limiter.limit("2 per hour;10/minute")
async def get_test(request):
    return response.text('test')
