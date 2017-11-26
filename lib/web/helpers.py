# -*- coding: utf-8 -*-
import os
import base64
from logging import debug
from sanic import response
from jinja2 import Environment, FileSystemLoader
from functools import wraps
THIS_DIR = os.path.dirname(os.path.abspath(__file__))

env = Environment(loader=FileSystemLoader(os.path.join(THIS_DIR, 'templates')), enable_async=True)
env.globals['auth'] = {'user': 'musicbot', 'password': 'musicbot'}


def check_auth(h):
    auth = env.globals['auth']
    s = auth['user'].encode() + b':' + auth['password'].encode()
    hash = base64.b64encode(s)
    basic = b'Basic ' + hash
    return basic == h.encode()


async def template(tpl, headers=None, **kwargs):
    template = env.get_template(tpl)
    rendered_template = await template.render_async(**kwargs)
    return response.html(rendered_template, headers=headers)


def basicauth(f):
    @wraps(f)
    async def wrapper(request, *args, **kwargs):
        headers = {}
        is_authorized = False
        if 'Authorization' not in request.headers:
            headers['WWW-Authenticate'] = 'Basic realm="musicbot"'
        else:
            auth = request.headers['Authorization']
            is_authorized = check_auth(auth)

        if is_authorized:
            debug('Authorization granted')
            return await f(request, *args, **kwargs)
        else:
            debug('Authorization denied')
            return response.json({'status': 'not_authorized'}, headers=headers, status=401)
    return wrapper
