# -*- coding: utf-8 -*-
from sanic import Blueprint, response
from aiocache import cached, SimpleMemoryCache
from aiocache.serializers import PickleSerializer
from aiocache.plugins import HitMissRatioPlugin, TimingPlugin
from . import helpers, forms
from .app import db
from logging import debug
collection = Blueprint('collection', strict_slashes=True, url_prefix='/collection')


@collection.get('/rescan')
@helpers.basicauth
async def rescan(request):
    return await helpers.template('rescan.html')


@collection.websocket('/progression')
@helpers.basicauth
async def progression(request, ws):
    while True:
        data = 'hello!'
        print('Sending: ' + data)
        await ws.send(data)
        data = await ws.recv()
        print('Received: ' + data)


@collection.get('/stats')
@helpers.basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer(), key='stats')
async def stats(request):
    '''Music library statistics'''
    mf = await helpers.get_filter(request)
    stats = await db.stats(mf)
    return await helpers.template('stats.html', stats=stats, mf=mf)


@collection.route('/generate')
@helpers.basicauth
async def generate(request):
    '''Generate a playlist step by step'''
    # precedent = request.form
    mf = helpers.get_filter(request, db)
    if request.args.get('play', False):
        musics = await db.musics(mf)
        return await helpers.template('player.html', musics=musics, mf=mf)
    if request.args.get('zip', False):
        musics = await db.musics(mf)
        return helpers.zip(musics)
    if request.args.get('m3u', False):
        musics = await db.musics(mf)
        return await helpers.m3u(musics)
    records = await db.form(mf)
    form = forms.FilterForm(obj=records)
    form.initialize(records)
    return await helpers.template('generate.html', form=form, mf=mf)


@collection.route('/consistency')
@helpers.basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def consistency(request):
    '''Consistency'''
    return response.text('not implemented')


@collection.route('/folders')
@helpers.basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer(), key='folders')
async def folders(request):
    '''Get filters'''
    folders = await db.folders_name()
    return await helpers.template('folders.html', folders=folders)


@collection.route('/filters')
@helpers.basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer(), key='filters')
async def filters(request):
    '''Get filters'''
    filters = await db.filters()
    return await helpers.template('filters.html', filters=filters)


@collection.route('/keywords')
@helpers.basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer(), key='keywords')
async def keywords(request):
    '''Get keywords'''
    mf = await helpers.get_filter(request)
    keywords = await db.keywords_name(mf)
    return await helpers.template('keywords.html', keywords=keywords, mf=mf)


@collection.route('/genres')
@helpers.basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer(), key='genres')
async def genres(request):
    '''List artists'''
    mf = await helpers.get_filter(request)
    genres = await db.genres_name(mf)
    return await helpers.template("genres.html", genres=genres, mf=mf)


@collection.route('/artists')
@helpers.basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer(), key='artists')
async def artists(request):
    '''List artists'''
    mf = await helpers.get_filter(request)
    artists = await db.artists_name(mf)
    return await helpers.template("artists.html", artists=artists, mf=mf)


@collection.route('/albums')
@helpers.basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer(), key='albums')
async def albums(request):
    '''List albums'''
    mf = await helpers.get_filter(request)
    albums = await db.albums_name(mf)
    return await helpers.template("albums.html", albums=albums, mf=mf)


@collection.route('/musics')
@helpers.basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer(), key='musics')
async def musics(request):
    '''List musics'''
    mf = await helpers.get_filter(request)
    musics = await db.musics(mf)
    return await helpers.template("musics.html", musics=musics, mf=mf)


@collection.route('/download')
@helpers.basicauth
async def download(request):
    '''Download a track'''
    music = await helpers.get_music(request)
    return helpers.send_file(music, name=helpers.download_title(music), attachment='attachment')


@collection.route('/listen')
@helpers.basicauth
async def listen(request):
    '''Listen a track'''
    music = await helpers.get_music(request)
    return helpers.send_file(music=music, name=helpers.download_title(music), attachment='inline')


@collection.route('/m3u')
@helpers.basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def m3u(request):
    '''Download m3u'''
    mf = await helpers.get_filter(request)
    musics = await db.musics(mf)
    name = request.args.get('name', 'playlist')
    return await helpers.m3u(musics, name)


@collection.route('/zip')
@helpers.basicauth
async def zip(request):
    '''Generate a playlist'''
    mf = await helpers.get_filter(request)
    musics = await db.musics(mf)
    if len(musics) == 0:
        return response.text('Empty playlist')
    name = request.args.get('name', 'archive')
    return helpers.zip(musics, name)


async def gen_playlist(request):
    mf = await helpers.get_filter(request)
    musics = await db.musics(mf)
    return await helpers.template('player.html', musics=musics, mf=mf)


@cached(cache=SimpleMemoryCache, serializer=PickleSerializer(), plugins=[HitMissRatioPlugin(), TimingPlugin()])
async def cached_call(f, request):
    return await f(request)


@collection.route('/player')
@helpers.basicauth
async def player(request):
    '''Play a playlist in browser'''
    if request.args.get('shuffle', False):
        debug('Shuffled playlist, not using cache')
        return await gen_playlist(request)
    return await cached_call(gen_playlist, request)
