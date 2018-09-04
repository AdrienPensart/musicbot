from sanic import response, Blueprint
from aiocache import cached, SimpleMemoryCache
from aiocache.serializers import PickleSerializer
from . import helpers
from .mfilter import WebFilter
from .app import db

api_v1 = Blueprint('api_v1', strict_slashes=True, url_prefix='/v1')
# from .limiter import limiter
# limiter.limit("2 per hour")(api_v1)


@api_v1.route('/stats')
@helpers.basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def stats(request):
    '''Music library statistics, APIv1'''
    mf = WebFilter(request)
    stats = await db.stats(mf, json=True)
    return response.HTTPResponse(stats, content_type="application/json")


@api_v1.route("/folders")
@helpers.basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def folders(request):
    '''Get filters'''
    folders = await db.folders(json=True)
    return response.HTTPResponse(folders, content_type="application/json")


@api_v1.route("/filters")
@helpers.basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def filters(request):
    '''Get filters'''
    filters = await db.filters(json=True)
    return response.HTTPResponse(filters, content_type="application/json")


@api_v1.route('/musics')
@helpers.basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def musics(request):
    '''List musics'''
    mf = await helpers.get_filter(request)
    musics = await db.musics(mf, json=True)
    return response.HTTPResponse(musics, content_type="application/json")


@api_v1.route("/playlist")
@helpers.basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def playlist(request):
    '''Generate a playlist, APIv1'''
    mf = await helpers.get_filter(request)
    musics = await db.musics(mf, json=True)
    return response.HTTPResponse(musics, content_type="application/json")


@api_v1.route('/artists')
@helpers.basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def artists(request):
    '''List artists'''
    mf = await helpers.get_filter(request)
    artists = await db.artists(mf, json=True)
    return response.HTTPResponse(artists, content_type="application/json")


@api_v1.route('/genres')
@helpers.basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def genres(request):
    '''List artists'''
    mf = await helpers.get_filter(request)
    genres = await db.genres(mf, json=True)
    return response.HTTPResponse(genres, content_type="application/json")


@api_v1.route('/albums')
@helpers.basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def albums(request):
    '''List albums'''
    mf = await helpers.get_filter(request)
    albums = await db.albums(mf, json=True)
    return response.HTTPResponse(albums, content_type="application/json")


@api_v1.route('/keywords')
@helpers.basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def keywords(request):
    '''Get keywords, APIv1'''
    mf = await helpers.get_filter(request)
    keywords = await db.keywords(mf, json=True)
    return response.HTTPResponse(keywords, content_type="application/json")
