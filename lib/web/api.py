# -*- coding: utf-8 -*-
from logging import debug
from sanic import response, Blueprint
from .app import app
from .filter import WebFilter
api_v1 = Blueprint('api_v1', url_prefix='/v1')


@api_v1.route('/stats')
async def stats(request):
    '''Music library statistics, APIv1'''
    db = app.config['CTX'].obj.db
    mf = WebFilter(request)
    stats = await db.stats(mf)
    debug(stats)
    return response.json(dict(stats))


@api_v1.route("/playlist")
async def playlist(request):
    '''Generate a playlist, APIv1'''
    db = app.config['CTX'].obj.db
    mf = WebFilter(request)
    musics = await db.filter(mf, True)
    return response.HTTPResponse(musics, content_type="application/json")
