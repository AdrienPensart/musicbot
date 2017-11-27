# -*- coding: utf-8 -*-
from logging import debug
from urllib.parse import unquote
from sanic import Blueprint
from aiocache import cached, SimpleMemoryCache
from aiocache.serializers import PickleSerializer
from .helpers import template
from .forms import FilterForm
from .app import app
from .filter import WebFilter
collection = Blueprint('collection', url_prefix='/collection')


@collection.route("/stats")
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def stats(request):
    '''Music library statistics'''
    db = app.config['DB']
    mf = WebFilter(request)
    stats = await db.stats(mf)
    debug(stats)
    return await template('stats.html', stats=stats)


@collection.route("/generate")
async def generate(request):
    db = app.config['DB']
    # precedent = request.form
    mf = WebFilter(request)
    records = await db.form(mf)
    form = FilterForm()
    form.initialize(records)
    return await template('generate.html', form=form)


@collection.route("/consistency")
async def consistency(request):
    return await template('consistency.html')


@collection.route("/keywords")
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def keywords(request):
    '''Get keywords'''
    db = app.config['DB']
    mf = WebFilter(request)
    keywords = await db.keywords(mf)
    debug(keywords)
    return await template('keywords.html', keywords=keywords)


@collection.route("/keywords/<keyword>")
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def keyword(request, keyword):
    '''List objects related to keyword'''
    db = app.config['DB']
    mf = WebFilter(request, keywords=[keyword])
    artists = await db.artists(mf)
    return await template("keyword.html", keyword=keyword, artists=artists)


@collection.route('/artists')
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def artists(request):
    '''List artists'''
    db = app.config['DB']
    mf = WebFilter(request)
    artists = await db.artists(mf)
    return await template("artists.html", artists=artists)


@collection.route('/<artist>')
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def albums(request, artist):
    '''List albums for artist'''
    artist = unquote(artist)
    db = app.config['DB']
    mf = WebFilter(request, artists=[artist])
    albums = await db.albums(mf)
    return await template("artist.html", artist=artist, albums=albums, keywords=mf.keywords)


@collection.route('/<artist>/<album>')
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def musics(request, artist, album):
    '''List tracks for artist/album'''
    artist = unquote(artist)
    album = unquote(album)
    db = app.config['DB']
    mf = WebFilter(request, artists=[artist], albums=[album])
    musics = await db.filter(mf)
    return await template("album.html", artist=artist, album=album, musics=musics)


@collection.route('/<artist>/<album>/<title>')
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


@collection.route("/playlist")
@cached(cache=SimpleMemoryCache, serializer=PickleSerializer())
async def playlist(request):
    '''Generate a playlist'''
    db = app.config['DB']
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
