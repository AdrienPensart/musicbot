# -*- coding: utf-8 -*-
from sanic import response, Blueprint
from aiocache import cached, SimpleMemoryCache
from aiocache.serializers import PickleSerializer
from . import helpers, filter
from .app import app

api_v1 = Blueprint('api_v1', url_prefix='/v1')
# from .limiter import limiter
# limiter.limit("2 per hour")(api_v1)


@api_v1.route('/stats', strict_slashes=True)
@helpers.basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def stats(request):
    '''Music library statistics, APIv1'''
    db = app.config['DB']
    mf = filter.WebFilter(request)
    stats = await db.stats(mf, json=True)
    return response.HTTPResponse(stats, content_type="application/json")


@api_v1.route("/folders", strict_slashes=True)
@helpers.basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def folders(request):
    '''Get filters'''
    db = app.config['DB']
    folders = await db.folders(json=True)
    return response.HTTPResponse(folders, content_type="application/json")


@api_v1.route("/filters", strict_slashes=True)
@helpers.basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def filters(request):
    '''Get filters'''
    db = app.config['DB']
    filters = await db.filters(json=True)
    return response.HTTPResponse(filters, content_type="application/json")


@api_v1.route('/musics', strict_slashes=True)
@helpers.basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def musics(request):
    '''List musics'''
    db = app.config['DB']
    mf = await helpers.get_filter(request, db)
    musics = await db.musics(mf, json=True)
    return response.HTTPResponse(musics, content_type="application/json")


@api_v1.route("/playlist", strict_slashes=True)
@helpers.basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def playlist(request):
    '''Generate a playlist, APIv1'''
    db = app.config['DB']
    mf = await helpers.get_filter(request, db)
    musics = await db.musics(mf, json=True)
    return response.HTTPResponse(musics, content_type="application/json")


@api_v1.route('/artists', strict_slashes=True)
@helpers.basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def artists(request):
    '''List artists'''
    db = app.config['DB']
    mf = await helpers.get_filter(request, db)
    artists = await db.artists(mf, json=True)
    return response.HTTPResponse(artists, content_type="application/json")


@api_v1.route('/genres', strict_slashes=True)
@helpers.basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def genres(request):
    '''List artists'''
    db = app.config['DB']
    mf = await helpers.get_filter(request, db)
    genres = await db.genres(mf, json=True)
    return response.HTTPResponse(genres, content_type="application/json")


@api_v1.route('/albums', strict_slashes=True)
@helpers.basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def albums(request):
    '''List albums'''
    db = app.config['DB']
    mf = await helpers.get_filter(request, db)
    albums = await db.albums(mf, json=True)
    return response.HTTPResponse(albums, content_type="application/json")


@api_v1.route("/keywords", strict_slashes=True)
@helpers.basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def keywords(request):
    '''Get keywords, APIv1'''
    db = app.config['DB']
    mf = await helpers.get_filter(request, db)
    keywords = await db.keywords(mf, json=True)
    return response.HTTPResponse(keywords, content_type="application/json")
