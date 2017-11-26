# -*- coding: utf-8 -*-
import os
import time
from sanic import response
from sanic.exceptions import RequestTimeout, abort
from sanic_openapi import swagger_blueprint, openapi_blueprint
from urllib.parse import unquote
from logging import debug
from aiocache import cached, SimpleMemoryCache
from aiocache.serializers import PickleSerializer
from .lib import bytesToHuman, secondsToHuman
from .helpers import timeit
from .web.filter import WebFilter
from .web.helpers import env, template, basicauth
from .web.forms import FilterForm
from .web.api import api_v1
from .web.app import app


def basename(path):
    return os.path.basename(path)


def get_flashed_messages():
    return ()


def download_title(m):
    return m['artist'] + ' - ' + m['album'] + ' - ' + basename(m['path'])


# app = Sanic(name='musicbot', log_config=None)
app.blueprint(api_v1)
app.blueprint(openapi_blueprint)
app.blueprint(swagger_blueprint)
app.config['WTF_CSRF_SECRET_KEY'] = 'top secret!'
env.globals['get_flashed_messages'] = get_flashed_messages
env.globals['url_for'] = app.url_for
env.globals['bytesToHuman'] = bytesToHuman
env.globals['secondsToHuman'] = secondsToHuman
env.globals['download_title'] = download_title
env.globals['request_time'] = lambda: time.time() - env.globals['request_start_time']
session = {}


@app.middleware('request')
@basicauth
@timeit
async def global_middleware(request):
    env.globals['request_start_time'] = time.time()
    request['session'] = session


@app.exception(RequestTimeout)
def timeout(request, exception):
    return response.text('RequestTimeout from error_handler.', 408)


@app.route("/collection/stats")
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def get_stats(request):
    '''Music library statistics'''
    db = app.config['CTX'].obj.db
    mf = WebFilter(request)
    stats = await db.stats(mf)
    debug(stats)
    return await template('stats.html', stats=stats)


@app.route("/collection/generate")
async def get_generate(request):
    db = app.config['CTX'].obj.db
    # precedent = request.form
    mf = WebFilter(request)
    records = await db.form(mf)
    form = FilterForm()
    form.initialize(records)
    return await template('generate.html', form=form)


@app.route("/collection/consistency")
async def get_consistency(request):
    return await template('consistency.html')


@app.route("/collection/keywords")
async def get_keywords(request):
    '''Get keywords'''
    db = app.config['CTX'].obj.db
    mf = WebFilter(request)
    keywords = await db.keywords(mf)
    debug(keywords)
    return await template('keywords.html', keywords=keywords)


@app.route("/collection/keywords/<keyword>")
async def get_keyword(request, keyword):
    '''List objects related to keyword'''
    db = app.config['CTX'].obj.db
    mf = WebFilter(request, keywords=[keyword])
    artists = await db.artists(mf)
    return await template("keyword.html", keyword=keyword, artists=artists)


@app.route('/collection/artists')
async def get_artists(request):
    '''List artists'''
    db = app.config['CTX'].obj.db
    mf = WebFilter(request)
    artists = await db.artists(mf)
    return await template("artists.html", artists=artists)


@app.route('/collection/<artist>')
async def get_albums(request, artist):
    '''List albums for artist'''
    artist = unquote(artist)
    db = app.config['CTX'].obj.db
    mf = WebFilter(request, artists=[artist])
    albums = await db.albums(mf)
    return await template("artist.html", artist=artist, albums=albums, keywords=mf.keywords)


@app.route('/collection/<artist>/<album>')
async def get_musics(request, artist, album):
    '''List tracks for artist/album'''
    artist = unquote(artist)
    album = unquote(album)
    db = app.config['CTX'].obj.db
    mf = WebFilter(request, artists=[artist], albums=[album])
    musics = await db.filter(mf)
    return await template("album.html", artist=artist, album=album, musics=musics)


@app.route('/collection/<artist>/<album>/<title>')
async def get_music(request, artist, album, title):
    '''Get a track tags or download it'''
    artist = unquote(artist)
    album = unquote(album)
    title = unquote(title)
    db = app.config['CTX'].obj.db
    mf = WebFilter(request, artists=[artist], albums=[album], titles=[title])
    musics = await db.filter(mf)
    if len(musics) != 1:
        return ('Music not found', 404)
    music = musics[0]
    return await template("music.html", music=music)


@app.route("/collection/playlist")
async def get_playlist(request):
    '''Generate a playlist'''
    db = app.config['CTX'].obj.db
    mf = WebFilter(request)
    musics = await db.filter(mf)
    return await template('playlist.html', headers={'Content-Type': 'text/plain; charset=utf-8'}, musics=musics)

    # downloadstr = request.args.get('download', '0')
    # listenstr = request.args.get('listen', '0')
    # name = request.args.get('name', 'archive')
    # debug("download? = {}, listen? = {}, name = {}, size = {}".format(downloadstr, listenstr, name, len(musics)))
    # # debug(musics)
    # if len(musics) == 0:
    #     return 'Empty playlist'
    # if listenstr in ['True', 'true', '1']:
    #     if len(musics) == 1:
    #         m = musics[0]
    #         debug("sending file: {}".format(m.path))
    #         return send_file(m.path, mimetype="audio/mpeg", attachment_filename=os.path.basename(m.path))
    #     else:
    #         bio = io.BytesIO()
    #         result = render_template("playlist.html", musics=musics, download_title=download_title)
    #         data = result.encode('utf-8')
    #         bio.write(data)
    #         bio.seek(0)
    #         return send_file(bio, as_attachment=True, attachment_filename=name+'.m3u')
    # elif downloadstr in ['True', 'true', '1']:
    #     filename = name + '.zip'
    #     filepath = os.path.join('/tmp', filename)
    #     if len(musics) == 1 and name == download_title(musics[0]):
    #         m = musics[0]
    #         debug("sending file: {}".format(m.path))
    #         return send_file(m.path, as_attachment=True, conditional=True, mimetype="audio/mpeg", attachment_filename=os.path.basename(m.path))

    #     totalsize = sum([m.size for m in musics])
    #     if totalsize > humanfriendly.parse_size("1G"):
    #         return 'Archive too big, do not break my server !'

    #     zf = zipfile.ZipFile(filepath, mode='w')
    #     try:
    #         for m in musics:
    #             debug("adding to archive: {}".format(m.path))
    #             zf.write(m.path, os.path.join(m.artist, m.album, os.path.basename(m.path)))
    #     finally:
    #         zf.close()
    #     return send_file(filepath, as_attachment=True, attachment_filename=filename)
    # else:
    #     resp = make_response(render_template("playlist.html", musics=musics, download_title=download_title))
    #     resp.headers['Content-Type'] = 'text/plain; charset=utf-8'
    #     return resp


@app.route("/favicon.ico")
def get_favicon(request):
    abort(404)


@app.route("/")
async def get_root(request):
    print(app.router.routes_all)
    return await template('index.html')
