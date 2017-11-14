# -*- coding: utf-8 -*-
from sanic import Sanic
from sanic.response import html
from sanic import response
from sanic.exceptions import RequestTimeout
from jinja2 import Environment, FileSystemLoader
from urllib.parse import unquote
from .filter import Filter
from .file import mysplit
from .lib import convert_rating, num
from logging import debug
import os
import time
import sys


def basename(path):
    return os.path.basename(path)


def get_flashed_messages():
    return ()


def download_title(m):
    return m.artist + ' - ' + m.album + ' - ' + basename(m.path)


app = Sanic()
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
enable_async = sys.version_info >= (3, 6)
env = Environment(loader=FileSystemLoader(os.path.join(THIS_DIR, 'templates')), enable_async=enable_async)
env.globals['get_flashed_messages'] = get_flashed_messages
env.globals['url_for'] = app.url_for
env.globals['download_title'] = download_title
env.globals['request_time'] = lambda: time.time() - env.globals['request_start_time']


def webfilter(request, mf=None):
    if mf is None:
        mf = Filter()

    youtube = request.args.get('youtube', getattr(mf, 'youtube'))
    if youtube == "2":
        mf.youtube = None
    elif youtube == "1":
        mf.youtube = True
    elif youtube == "0":
        mf.youtube = False
    else:
        debug("BAD VALUE: {} {}".format(type(youtube), youtube))
    debug('youtube: {} {}'.format(youtube, mf.youtube))

    mf.shuffle = request.args.get('shuffle', getattr(mf, 'shuffle'))
    debug('shuffle : {}'.format(mf.shuffle))
    mf.relative = request.args.get('relative', getattr(mf, 'relative'))
    debug('relative: {}'.format(mf.relative))

    for param in ['formats', 'no_formats', 'artists', 'no_artists', 'genres', 'no_genres', 'albums', 'no_albums', 'titles', 'no_titles', 'keywords', 'no_keywords']:
        raw = request.args.get(param, getattr(mf, param))
        data = mysplit(raw, '","')
        if len(data) == 1 and data[0].startswith('"') and data[0].endswith('"'):
            data[0] = data[0][1:-1]
        debug('{} {}'.format(param, data))
        setattr(mf, param, data)

    for param in ['min_rating', 'max_rating']:
        data = convert_rating(request.args.get(param, getattr(mf, param)))
        debug('{} {}'.format(param, data))
        setattr(mf, param, data)

    for param in ['limit', 'min_size', 'max_size', 'min_duration', 'min_duration']:
        data = num(request.args.get(param, getattr(mf, param)))
        debug('{} {}'.format(param, data))
        setattr(mf, param, data)

    debug('Filter: {}'.format(mf.to_list()))
    return mf


@app.middleware('request')
async def set_request_start(request):
    env.globals['request_start_time'] = time.time()


async def template(tpl, **kwargs):
    template = env.get_template(tpl)
    rendered_template = await template.render_async(**kwargs)
    return html(rendered_template)


@app.exception(RequestTimeout)
def timeout(request, exception):
    return response.text('RequestTimeout from error_handler.', 408)


@app.route("/stats")
async def get_stats(request):
    return await template('stats.html')


@app.route("/generate")
async def get_generate(request):
    return await template('generate.html')


@app.route("/consistency")
async def get_consistency(request):
    return await template('consistency.html')


@app.route("/keywords")
async def get_keywords(request):
    '''Get keywords'''
    db = app.config['CTX'].obj.db
    mf = webfilter(request)
    keywords = await db.keywords(mf)
    # return json(keywords)
    debug(keywords)
    return await template('keywords.html', keywords=keywords)


@app.route("/keywords/<keyword>")
async def get_keyword(request, keyword):
    '''List objects related to keyword'''
    db = app.config['CTX'].obj.db
    mf = Filter(keywords=[keyword])
    mf = webfilter(request, mf)
    artists = await db.artists(mf)
    return await template("keyword.html", keyword=keyword, artists=artists)


@app.route('/artists')
async def get_artists(request):
    '''List artists'''
    db = app.config['CTX'].obj.db
    mf = webfilter(request)
    artists = await db.artists(mf)
    return await template("artists.html", artists=artists)


@app.route('/<artist>')
async def get_albums(request, artist):
    '''List albums for artist'''
    artist = unquote(artist)
    db = app.config['CTX'].obj.db
    mf = Filter(artists=[artist])
    mf = webfilter(request, mf)
    albums = await db.albums(mf)
    return await template("artist.html", artist=artist, albums=albums, keywords=mf.keywords)


@app.route('/<artist>/<album>')
async def get_musics(request, artist, album):
    '''List tracks for artist/album'''
    artist = unquote(artist)
    album = unquote(album)
    db = app.config['CTX'].obj.db
    mf = Filter(artists=[artist], albums=[album])
    mf = webfilter(request, mf)
    musics = await db.filter(mf)
    return await template("album.html", artist=artist, album=album, musics=musics)


@app.route('/<artist>/<album>/<title>')
async def get_music(request, artist, album, title):
    '''Get a track tags or download it'''
    artist = unquote(artist)
    album = unquote(album)
    title = unquote(title)
    db = app.config['CTX'].obj.db
    mf = Filter(artists=[artist], albums=[album], titles=[title])
    mf = webfilter(request, mf)
    musics = await db.filter(mf)
    if len(musics) != 1:
        return ('Music not found', 404)
    music = musics[0]
    return await template("music.html", music=music)


@app.route("/playlist")
async def get_playlist(request):
    '''Generate a playlist'''
    db = app.config['CTX'].obj.db
    mf = webfilter(request)
    musics = await db.filter(mf)
    return await template('playlist.html', musics)

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
    return ("", 404)


@app.route("/")
async def get_root(request):
    return await template('index.html')
