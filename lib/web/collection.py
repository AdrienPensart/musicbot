# -*- coding: utf-8 -*-
from sanic import Blueprint, response
from aiocache import cached, SimpleMemoryCache
from aiocache.serializers import PickleSerializer
from . import helpers, forms, filter
from .app import app
collection = Blueprint('collection', url_prefix='/collection')


@collection.get("/stats", strict_slashes=True)
@helpers.basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def stats(request):
    '''Music library statistics'''
    db = app.config['DB']
    mf = filter.WebFilter(request)
    stats = await db.stats(mf)
    return await helpers.template('stats.html', stats=stats, mf=mf)


@collection.route("/generate", strict_slashes=True)
@helpers.basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def generate(request):
    '''Generate a playlist step by step'''
    db = app.config['DB']
    # precedent = request.form
    mf = filter.WebFilter(request)
    if request.args.get('play', False):
        musics = await db.filter(mf)
        return await helpers.template('player.html', musics=musics, mf=mf)
    if request.args.get('zip', False):
        musics = await db.filter(mf)
        return helpers.zip(musics)
    if request.args.get('m3u', False):
        musics = await db.filter(mf)
        return await helpers.m3u(musics)
    records = await db.form(mf)
    form = forms.FilterForm(obj=records)
    form.initialize(records)
    return await helpers.template('generate.html', form=form, mf=mf)


@collection.route("/consistency", strict_slashes=True)
@helpers.basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def consistency(request):
    '''Consistency'''
    return response.text('not implemented')


@collection.route("/keywords", strict_slashes=True)
@helpers.basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def keywords(request):
    '''Get keywords'''
    db = app.config['DB']
    mf = filter.WebFilter(request)
    keywords = await db.keywords(mf)
    return await helpers.template('keywords.html', keywords=keywords, mf=mf)


@collection.route('/genres', strict_slashes=True)
@helpers.basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def genres(request):
    '''List artists'''
    db = app.config['DB']
    mf = filter.WebFilter(request)
    genres = await db.genres(mf)
    return await helpers.template("genres.html", genres=genres, mf=mf)


@collection.route('/artists', strict_slashes=True)
@helpers.basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def artists(request):
    '''List artists'''
    db = app.config['DB']
    mf = filter.WebFilter(request)
    artists = await db.artists(mf)
    return await helpers.template("artists.html", artists=artists, mf=mf)


@collection.route('/albums', strict_slashes=True)
@helpers.basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def albums(request):
    '''List albums'''
    db = app.config['DB']
    mf = filter.WebFilter(request)
    albums = await db.albums_name(mf)
    return await helpers.template("albums.html", albums=albums, mf=mf)


@collection.route('/musics', strict_slashes=True)
@helpers.basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def musics(request):
    '''List musics'''
    db = app.config['DB']
    mf = filter.WebFilter(request)
    musics = await db.filter(mf)
    return await helpers.template("musics.html", musics=musics, mf=mf)


async def get_music(request):
    db = app.config['DB']
    mf = filter.WebFilter(request, limit=1)
    musics = await db.filter(mf)
    if not len(musics):
        return ('music not found', 404)
    return musics[0]


@collection.route('/download', strict_slashes=True)
@helpers.basicauth
async def download(request):
    '''Download a track'''
    music = await get_music(request)
    return helpers.send_file(music, name=helpers.download_title(music), attachment='attachment')


@collection.route("/listen", strict_slashes=True)
@helpers.basicauth
async def listen(request):
    '''Listen a track'''
    music = await get_music(request)
    return helpers.send_file(music=music, name=helpers.download_title(music), attachment='inline')


@collection.route("/m3u", strict_slashes=True)
@helpers.basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def m3u(request):
    '''Download m3u'''
    db = app.config['DB']
    mf = filter.WebFilter(request)
    musics = await db.filter(mf)
    name = request.args.get('name', 'playlist')
    return await helpers.m3u(musics, name)


@collection.route("/zip", strict_slashes=True)
@helpers.basicauth
async def zip(request):
    '''Generate a playlist'''
    db = app.config['DB']
    mf = filter.WebFilter(request)
    musics = await db.filter(mf)
    if len(musics) == 0:
        return response.text('Empty playlist')
    name = request.args.get('name', 'archive')
    return helpers.zip(musics, name)


@collection.route("/player", strict_slashes=True)
@helpers.basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def player(request):
    '''Play a playlist in browser'''
    db = app.config['DB']
    mf = filter.WebFilter(request)
    musics = await db.filter(mf)
    return await helpers.template('player.html', musics=musics, mf=mf)
