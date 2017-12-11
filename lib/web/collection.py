# -*- coding: utf-8 -*-
from logging import debug
from urllib.parse import quote, unquote
from sanic import Blueprint, response
from aiocache import cached, SimpleMemoryCache
from aiocache.serializers import PickleSerializer
from .helpers import template, download_title, basicauth
from .forms import FilterForm
from .app import app
from .filter import WebFilter
collection = Blueprint('collection', url_prefix='/collection')


@collection.route("/stats", strict_slashes=True)
@basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def stats(request):
    '''Music library statistics'''
    db = app.config['DB']
    mf = WebFilter(request)
    stats = await db.stats(mf)
    debug(stats)
    return await template('stats.html', stats=stats)


@collection.route("/generate", strict_slashes=True)
@basicauth
async def generate(request):
    db = app.config['DB']
    # precedent = request.form
    mf = WebFilter(request)
    records = await db.form(mf)
    form = FilterForm()
    form.initialize(records)
    return await template('generate.html', form=form)


@collection.route("/consistency", strict_slashes=True)
@basicauth
async def consistency(request):
    return await template('consistency.html')


@collection.route("/keywords", strict_slashes=True)
@basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def keywords(request):
    '''Get keywords'''
    db = app.config['DB']
    mf = WebFilter(request)
    keywords = await db.keywords(mf)
    debug(keywords)
    return await template('keywords.html', keywords=keywords)


@collection.route("/keywords/<keyword>", strict_slashes=True)
@basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def keyword(request, keyword):
    '''List objects related to keyword'''
    db = app.config['DB']
    mf = WebFilter(request, keywords=[keyword])
    artists = await db.artists(mf)
    return await template("keyword.html", keyword=keyword, artists=artists)


@collection.route('/artists', strict_slashes=True)
@basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def artists(request):
    '''List artists'''
    db = app.config['DB']
    mf = WebFilter(request)
    artists = await db.artists(mf)
    return await template("artists.html", artists=artists)


@collection.route('/<artist>', strict_slashes=True)
@basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def albums(request, artist):
    '''List albums for artist'''
    artist = unquote(artist)
    db = app.config['DB']
    mf = WebFilter(request, artists=[artist])
    albums = await db.albums(mf)
    return await template("artist.html", artist=artist, albums=albums, keywords=mf.keywords)


@collection.route('/<artist>/<album>', strict_slashes=True)
@basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def musics(request, artist, album):
    '''List tracks for artist/album'''
    artist = unquote(artist)
    album = unquote(album)
    db = app.config['DB']
    mf = WebFilter(request, artists=[artist], albums=[album])
    musics = await db.filter(mf)
    return await template("album.html", artist=artist, album=album, musics=musics)


@collection.route('/<artist>/<album>/<title>', strict_slashes=True)
@basicauth
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def music(request, artist, album, title):
    '''Get a track tags or download it'''
    artist = unquote(artist)
    album = unquote(album)
    title = unquote(title)
    db = app.config['DB']
    mf = WebFilter(request, artists=[artist], albums=[album], titles=[title])
    musics = await db.filter(mf)
    if len(musics) != 1:
        return ('Music not found', 404)
    music = musics[0]
    return await template("music.html", music=music)


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


@collection.route("/playlist", strict_slashes=True)
@basicauth
# @cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def playlist(request, noauth=True):
    '''Generate a playlist'''
    db = app.config['DB']
    mf = WebFilter(request)
    musics = await db.filter(mf)

    downloadstr = request.args.get('download', '0')
    listenstr = request.args.get('listen', '0')
    name = request.args.get('name', 'archive')
    debug("download? = {}, listen? = {}, name = {}, size = {}".format(downloadstr, listenstr, name, len(musics)))
    if len(musics) == 0:
        return response.text('Empty playlist')
    if listenstr in ['True', 'true', '1']:
        if len(musics) == 1:
            return send_file(music=musics[0], name=name, attachment='inline')
        else:
            headers = {}
            headers['Content-Disposition'] = '{}; filename={}'.format('attachment', name + '.m3u')
            return await template("playlist.html", headers=headers, musics=musics)
    if downloadstr in ['True', 'true', '1']:
        if len(musics) == 1 and name == download_title(musics[0]):
            return send_file(music=musics[0], name=name, attachment='attachment')
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
    return await template('playlist.html', headers={'Content-Type': 'text/plain; charset=utf-8'}, musics=musics)
