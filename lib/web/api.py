# -*- coding: utf-8 -*-
from logging import debug
from sanic import response, Blueprint
from aiocache import cached, SimpleMemoryCache
from aiocache.serializers import PickleSerializer
from .app import app
from .filter import WebFilter
api_v1 = Blueprint('api_v1', url_prefix='/v1')


@api_v1.route('/stats')
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def stats(request):
    '''Music library statistics, APIv1'''
    db = app.config['DB']
    mf = WebFilter(request)
    stats = await db.stats(mf)
    debug(stats)
    return response.json(dict(stats))


@api_v1.route("/playlist")
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def playlist(request):
    '''Generate a playlist, APIv1'''
    db = app.config['DB']
    mf = WebFilter(request)
    musics = await db.filter(mf, True)
    debug(musics)
    return response.HTTPResponse(musics, content_type="application/json")


@api_v1.route('/artists')
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def artists(request):
    '''List artists'''
    db = app.config['DB']
    mf = WebFilter(request)
    artists = await db.artists(mf)
    return response.json(artists)


@api_v1.route("/keywords")
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def keywords(request):
    '''Get keywords, APIv1'''
    db = app.config['DB']
    mf = WebFilter(request)
    keywords = await db.keywords(mf)
    debug(keywords)
    return response.json(keywords)