# -*- coding: utf-8 -*-
import os
import base64
import logging
import asyncio
from urllib.parse import quote
from sanic import response
from jinja2 import Environment, FileSystemLoader
from functools import wraps
from .mfilter import WebFilter
from .config import webconfig
from .app import db

logger = logging.getLogger(__name__)

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

env = Environment(extensions=['jinja2.ext.loopcontrols'], loader=FileSystemLoader(os.path.join(THIS_DIR, 'templates')), enable_async=True, autoescape=True)


async def get_filter(request, **kwargs):
    filter_name = request.args.get('filter', None)
    d = kwargs
    if filter_name is not None:
        d = dict(await db.get_filter(filter_name))
    return WebFilter(request, **d)


async def get_music(request):
    mf = await get_filter(request, limit=1)
    musics = await db.musics(mf)
    if not len(musics):
        return ('music not found', 404)
    return musics[0]


async def m3u(musics, name='playlist'):
    headers = {}
    headers['Content-Disposition'] = 'attachment; filename={}'.format(name + '.m3u')
    return await template("m3u.html", headers=headers, musics=musics)


def zip(musics, name='archive'):
    headers = {}
    headers['X-Archive-Files'] = 'zip'
    headers['Content-Disposition'] = 'attachment; filename={}'.format(name + '.zip')
    # see mod_zip documentation :p
    lines = [' '.join(['-',
                       str(m['size']),
                       quote("/sendfile" + m['path'][len(m['folder']):]),
                       os.path.join(m['artist'], m['album'], os.path.basename(m['path']))])
             for m in musics]
    body = '\n'.join(lines)
    logger.debug(body)
    return response.HTTPResponse(headers=headers, body=body)


def send_file(music, name, attachment):
    logger.debug("sending file: {}".format(music['path']))
    headers = {}
    headers['Content-Description'] = 'File Transfer'
    # headers['Cache-Control'] = 'no-cache'
    headers['Cache-Control'] = 'public, must-revalidate'

    if music['path'].endswith('.flac'):
        headers['Content-Type'] = 'audio/flac'
    else:
        headers['Content-Type'] = 'audio/mpeg'

    headers['Content-Disposition'] = '{}; filename={}'.format(attachment, quote(name))
    headers['Accept-Ranges'] = 'bytes'
    headers['Content-Length'] = music['size']
    headers['Content-Transfer-Encoding'] = 'binary'
    headers['X-Accel-Buffering'] = 'no'
    server_path = "/sendfile" + music['path'][len(music['folder']):]
    logger.debug('server_path: {}'.format(server_path))
    headers['X-Accel-Redirect'] = server_path
    return response.HTTPResponse(headers=headers)


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
        if webconfig.no_auth:
            if asyncio.iscoroutinefunction(f):
                return await f(request, *args, **kwargs)
            return f(request, *args, **kwargs)

        headers = {}
        is_authorized = False
        if 'Authorization' not in request.headers:
            headers['WWW-Authenticate'] = 'Basic realm="musicbot"'
        else:
            auth = request.headers['Authorization']
            is_authorized = check_auth(auth)

        if is_authorized:
            logger.debug('Authorization granted')
            if asyncio.iscoroutinefunction(f):
                return await f(request, *args, **kwargs)
            return f(request, *args, **kwargs)
        else:
            logger.debug('Authorization denied')
            return response.json({'status': 'not_authorized'}, headers=headers, status=401)
    return wrapper
