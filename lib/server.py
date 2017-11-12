# -*- coding: utf-8 -*-
from sanic import Sanic
from sanic.response import html
from sanic import response
from sanic.exceptions import RequestTimeout
from jinja2 import Environment, FileSystemLoader
import os
import time
import sys


def get_flashed_messages():
    return ()


app = Sanic()
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
enable_async = sys.version_info >= (3, 6)
env = Environment(loader=FileSystemLoader(os.path.join(THIS_DIR, 'templates')), enable_async=enable_async)
env.globals['get_flashed_messages'] = get_flashed_messages
env.globals['url_for'] = app.url_for
env.globals['request_time'] = lambda: time.time() - env.globals['request_start_time']


@app.middleware('request')
async def set_request_start(request):
    env.globals['request_start_time'] = time.time()


async def template(tpl, **kwargs):
    template = env.get_template(tpl)
    rendered_template = await template.render_async(**kwargs)
    return html(rendered_template)


@app.exception(RequestTimeout)
def timeout(request, exception):
    return response.text('RequestTimeout from error_handler.', 408)


@app.route("/stats")
async def get_stats():
    return await template('stats.html')


@app.route("/artists")
async def get_artists():
    return await template('stats.html')


@app.route("/generate")
async def get_generate():
    return await template('generate.html')


@app.route("/consistency")
async def get_consistency():
    return await template('consistency.html')


@app.route("/keywords")
async def get_keywords():
    return await template('keywords.html')


@app.route("/favicon.ico")
def get_favicon():
    return ("", 404)


@app.route("/")
async def get_root(request):
    return await template('index.html')
