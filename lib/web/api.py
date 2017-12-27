# -*- coding: utf-8 -*-
from logging import debug, info
from sanic import response, Blueprint
from aiocache import cached, SimpleMemoryCache
from aiocache.serializers import PickleSerializer
from . import helpers, filter
from .app import app

api_v1 = Blueprint('api_v1', url_prefix='/v1')
# from .limiter import limiter
# limiter.limit("2 per hour")(api_v1)


@api_v1.route('/rescan', strict_slashes=True)
@helpers.basicauth
async def rescan(request):
    '''Rescan music library, APIv1'''
    db = app.config['DB']
    folders = await db.folders()
    for folder in folders:
        info('rescanning {}'.format(folder))
    return response.json(dict(stats))


@api_v1.route('/musics', strict_slashes=True)
@helpers.basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def musics(request):
    '''List musics'''
    db = app.config['DB']
    mf = filter.WebFilter(request)
    musics = await db.filter(mf, json=True)
    return response.HTTPResponse(musics, content_type="application/json")


@api_v1.route('/stats', strict_slashes=True)
@helpers.basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def stats(request):
    '''Music library statistics, APIv1'''
    db = app.config['DB']
    mf = filter.WebFilter(request)
    stats = await db.stats(mf)
    debug(stats)
    return response.json(dict(stats))


@api_v1.route("/playlist", strict_slashes=True)
@helpers.basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def playlist(request):
    '''Generate a playlist, APIv1'''
    db = app.config['DB']
    mf = filter.WebFilter(request)
    musics = await db.filter(mf, json=True)
    return response.HTTPResponse(musics, content_type="application/json")


@api_v1.route('/artists', strict_slashes=True)
@helpers.basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def artists(request):
    '''List artists'''
    db = app.config['DB']
    mf = filter.WebFilter(request)
    artists = await db.artists(mf)
    return response.json(artists)


@api_v1.route('/genres', strict_slashes=True)
@helpers.basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def genres(request):
    '''List artists'''
    db = app.config['DB']
    mf = filter.WebFilter(request)
    genres = await db.genres(mf)
    return response.json(genres)


@api_v1.route("/keywords", strict_slashes=True)
@helpers.basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def keywords(request):
    '''Get keywords, APIv1'''
    db = app.config['DB']
    mf = filter.WebFilter(request)
    keywords = await db.keywords(mf)
    debug(keywords)
    return response.json(keywords)
