# -*- coding: utf-8 -*-
import os
import base64
from logging import debug
from sanic import response
from jinja2 import Environment, FileSystemLoader
from functools import wraps
THIS_DIR = os.path.dirname(os.path.abspath(__file__))

env = Environment(extensions=['jinja2.ext.loopcontrols'], loader=FileSystemLoader(os.path.join(THIS_DIR, 'templates')), enable_async=True)
env.globals['auth'] = {'user': 'musicbot', 'password': 'musicbot'}


def send_file(music, name, attachment='attachment'):
    debug("sending file: {}".format(music['path']))
    headers = {}
    headers['Content-Description'] = 'File Transfer'
    headers['Cache-Control'] = 'no-cache'
    headers['Content-Type'] = 'audio/mpeg'
    headers['Content-Disposition'] = '{}; filename={}'.format(attachment, name)
    headers['Content-Length'] = music['size']
    server_path = "/download" + music['path'][len(music['folder']):]
    debug('server_path: {}'.format(server_path))
    headers['X-Accel-Redirect'] = server_path
    return response.HTTPResponse(headers=headers)


def server():
    return env.globals['auth']['user'] + ':' + env.globals['auth']['password'] + '@' + env.globals['server_name']


def basename(path):
    return os.path.basename(path)


def get_flashed_messages():
    return ()


def download_title(m):
    _, extension = os.path.splitext(m['path'])
    return m['artist'] + ' - ' + m['album'] + ' - ' + m['title'] + extension


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
