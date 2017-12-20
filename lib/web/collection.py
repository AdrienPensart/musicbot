# -*- coding: utf-8 -*-
from logging import debug
from urllib.parse import quote
from sanic import Blueprint, response
from aiocache import cached, SimpleMemoryCache
from aiocache.serializers import PickleSerializer
from .helpers import download_title, template, basicauth, send_file
from .forms import FilterForm
from .app import app
from .filter import WebFilter
collection = Blueprint('collection', url_prefix='/collection')


@collection.get("/stats", strict_slashes=True)
@basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def stats(request):
    '''Music library statistics'''
    db = app.config['DB']
    mf = WebFilter(request)
    stats = await db.stats(mf)
    return await template('stats.html', stats=stats)


@collection.route("/generate", strict_slashes=True)
@basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def generate(request):
    '''Generate a playlist step by step'''
    db = app.config['DB']
    # precedent = request.form
    mf = WebFilter(request)
    records = await db.form(mf)
    form = FilterForm(obj=records)
    # form.initialize(records)
    return await template('generate.html', form=form)


@collection.route("/consistency", strict_slashes=True)
@basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def consistency(request):
    '''Consistency'''
    return response.text('not implemented')


@collection.route("/keywords", strict_slashes=True)
@basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def keywords(request):
    '''Get keywords'''
    db = app.config['DB']
    mf = WebFilter(request)
    keywords = await db.keywords(mf)
    return await template('keywords.html', keywords=keywords)


@collection.route('/genres', strict_slashes=True)
@basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def genres(request):
    '''List artists'''
    db = app.config['DB']
    mf = WebFilter(request)
    genres = await db.genres(mf)
    return await template("genres.html", genres=genres)


@collection.route('/artists', strict_slashes=True)
@basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def artists(request):
    '''List artists'''
    db = app.config['DB']
    mf = WebFilter(request)
    artists = await db.artists(mf)
    return await template("artists.html", artists=artists)


@collection.route('/albums', strict_slashes=True)
@basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def albums(request):
    '''List albums'''
    db = app.config['DB']
    mf = WebFilter(request)
    albums = await db.albums(mf)
    return await template("albums.html", albums=albums)


@collection.route('/musics', strict_slashes=True)
@basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def musics(request):
    '''List musics'''
    db = app.config['DB']
    mf = WebFilter(request)
    musics = await db.filter(mf)
    return await template("musics.html", musics=musics)


async def get_music(request):
    db = app.config['DB']
    mf = WebFilter(request, limit=1)
    musics = await db.filter(mf)
    if not len(musics):
        return ('music not found', 404)
    return musics[0]


@collection.route('/download', strict_slashes=True)
@basicauth
async def download(request):
    '''Download a track'''
    music = await get_music(request)
    return send_file(music, name=download_title(music))


@collection.route("/listen", strict_slashes=True)
@basicauth
async def listen(request):
    '''Listen a track'''
    music = await get_music(request)
    return send_file(music=music, name=download_title(music), attachment='inline')


@collection.route("/m3u", strict_slashes=True)
@basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def m3u(request):
    '''Download m3u'''
    db = app.config['DB']
    mf = WebFilter(request)
    musics = await db.filter(mf)
    name = request.args.get('name', 'playlist')
    headers = {}
    headers['Content-Disposition'] = 'attachment; filename={}'.format(name + '.m3u')
    return await template("m3u.html", headers=headers, musics=musics)


@collection.route("/zip", strict_slashes=True)
@basicauth
async def zip(request):
    '''Generate a playlist'''
    db = app.config['DB']
    mf = WebFilter(request)
    musics = await db.filter(mf)
    if len(musics) == 0:
        return response.text('Empty playlist')

    name = request.args.get('name', 'archive')
    headers = {}
    headers['X-Archive-Files'] = 'zip'
    headers['Content-Disposition'] = 'attachment; filename={}'.format(name + '.zip')
    import os
    # see mod_zip documentation :p
    lines = [' '.join(['-',
                       str(m['size']),
                       quote("/download" + m['path'][len(m['folder']):]),
                       os.path.join(m['artist'], m['album'], os.path.basename(m['path']))])
             for m in musics]
    body = '\n'.join(lines)
    debug(body)
    return response.HTTPResponse(headers=headers, body=body)


@collection.route("/player", strict_slashes=True)
@basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def player(request):
    '''Play a playlist in browser'''
    db = app.config['DB']
    mf = WebFilter(request)
    musics = await db.filter(mf)
    return await template('player.html', musics=musics)
