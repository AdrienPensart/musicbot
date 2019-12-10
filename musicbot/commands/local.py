import logging
import os
import codecs
import csv
import json
import datetime
from textwrap import indent
import click
import vlc
from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.application import run_in_terminal, get_app
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit import HTML, print_formatted_text
from tqdm import tqdm
from prettytable import PrettyTable
from musicbot import lib, helpers, user
from musicbot.music import mfilter
from musicbot.config import config
from musicbot.music.file import File, supported_formats
from musicbot.music.fingerprint import acoustid_apikey_option


logger = logging.getLogger(__name__)
logging.getLogger("vlc").setLevel(logging.NOTSET)


@click.group(cls=helpers.GroupWithHelp)
@click.pass_context
@helpers.add_options(user.auth_options)
def cli(ctx, **kwargs):
    '''Local music management'''
    ctx.obj.u = lambda: user.User.new(**kwargs)


@cli.command()
@click.pass_context
@helpers.add_options(helpers.output_option)
def artists(ctx, output):
    '''List artists'''
    if output == 'table':
        pt = PrettyTable()
        pt.field_names = ["Name"]
        for a in ctx.obj.u().artists:
            pt.add_row([a['name']])
        print(pt)
    elif output == 'json':
        print(json.dumps(ctx.obj.u().artists))


@cli.command()
@click.pass_context
def load_filters(ctx):
    '''Load default filters'''
    ctx.obj.u().load_default_filters()


@cli.command()
@click.pass_context
@helpers.add_options(helpers.output_option)
def filters(ctx, output):
    '''List filters'''
    if output == 'json':
        print(json.dumps(ctx.obj.u().filters))
    elif output == 'table':
        pt = PrettyTable()
        pt.field_names = ["Name", "Keywords", "No keywords", "Min rating", "Max rating"]
        for f in ctx.obj.u().filters:
            pt.add_row([f['name'], f['keywords'], f['noKeywords'], f['minRating'], f['maxRating']])
        print(pt)


@cli.command()
@click.pass_context
@helpers.add_options(helpers.output_option)
@click.argument('name')
def filter(ctx, name, output):
    '''Print a filter'''
    f = ctx.obj.u().filter(name)
    if output == 'json':
        print(json.dumps(f))
    elif output == 'table':
        print(f)


@cli.command()
@click.pass_context
@helpers.add_options(helpers.output_option + mfilter.options)
def tracks(ctx, output, **kwargs):
    '''List tracks'''
    mf = mfilter.Filter(**kwargs)
    tracks = ctx.obj.u().do_filter(mf)
    if output == 'json':
        print(json.dumps(tracks))
    elif output == 'table':
        pt = PrettyTable()
        pt.field_names = [
            "Title",
            "Album",
            "Artist",
            # "Genre",
            # "Folder",
            # "Youtube",
            # "Spotify",
            # "Number",
            # "Path",
            # "Rating",
            # "Duration",
            # "Size",
            "Keywords"
        ]
        for t in tracks:
            pt.add_row([t['title'], t['album'], t['artist'], t['keywords']])
        print(pt)


@cli.command()
@click.pass_context
@helpers.add_options(helpers.output_option + mfilter.options)
def stats(ctx, output, **kwargs):
    '''Generate some stats for music collection with filters'''
    mf = mfilter.Filter(**kwargs)
    stats = ctx.obj.u().do_stat(mf)
    if output == 'json':
        print(json.dumps(stats))
    elif output == 'table':
        pt = PrettyTable()
        pt.field_names = ["Stat", "Value"]
        pt.add_row(["Music", stats['musics']])
        pt.add_row(["Artist", stats['artists']])
        pt.add_row(["Album", stats['albums']])
        pt.add_row(["Genre", stats['genres']])
        pt.add_row(["Keywords", stats['keywords']])
        pt.add_row(["Size", lib.bytes_to_human(int(stats['size']))])
        pt.add_row(["Total duration", datetime.timedelta(seconds=int(stats['duration']))])
        print(pt)


@cli.command()
@click.pass_context
@helpers.add_options(helpers.output_option)
def folders(ctx, output):
    '''List folders'''
    _folders = ctx.obj.u().folders
    if output == 'json':
        print(json.dumps(_folders))
    elif output == 'table':
        pt = PrettyTable()
        pt.field_names = ["Folder"]
        for f in _folders:
            pt.add_row([f])
        print(pt)


@cli.command()
@click.argument('folders', nargs=-1)
@click.pass_context
def scan(ctx, folders):
    '''(re)Load musics'''
    u = ctx.obj.u()
    if not folders:
        folders = u.folders
    files = helpers.genfiles(folders)
    u.bulk_insert(files)


@cli.command()
@click.argument('folders', nargs=-1)
@click.pass_context
def find(ctx, folders):
    '''Just list music files'''
    u = ctx.obj.u()
    if not folders:
        folders = u.folders

    files = lib.find_files(folders, supported_formats)
    for f in files:
        print(f[1])


@cli.command('csv')
@click.argument('path', type=click.File('w'), default='-')
@click.pass_context
def _csv(ctx, path):
    '''Export music files to csv file'''
    u = ctx.obj.u()
    folders = u.folders

    logger.info('Scanning folders: %s', folders)
    files = helpers.genfiles(folders)

    musicwriter = csv.writer(path, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    for f in files:
        musicwriter.writerow(f.ordered_dict().values())


@cli.command()
@click.pass_context
def watch(ctx):
    '''Watch files changes in folders'''
    ctx.obj.u().watch()


@cli.command()
@click.argument('folders', nargs=-1)
@helpers.add_options(helpers.concurrency_options + helpers.dry_option)
def flac2mp3(folders, concurrency, dry):
    '''Convert all files in folders to mp3'''
    import atexit
    import concurrent.futures as cf
    from concurrent.futures.thread import _python_exit
    from pydub import AudioSegment
    flac_files = list(lib.find_files(folders, ['flac']))

    pbar = None
    if not config.quiet:
        pbar = click.progressbar(length=len(flac_files), label='Converting musics')

    def convert(flac_path):
        logger.debug('Converting %s', flac_path)
        flac_audio = AudioSegment.from_file(flac_path, "flac")
        mp3_path = flac_path.replace('.flac', '.mp3')
        if not dry:
            flac_audio.export(mp3_path, format="mp3")
        else:
            logger.info("[DRY-RUN] Exporting from %s to %s", flac_path, mp3_path)
        if pbar:
            pbar.update(1)
    # Permit CTRL+C to work as intended
    atexit.unregister(_python_exit)  # pylint: disable=protected-access
    with cf.ThreadPoolExecutor(max_workers=concurrency) as executor:
        executor.shutdown = lambda wait: None
        futures = [executor.submit(convert, flac_path) for flac_path in flac_files]
        cf.wait(futures)


@cli.command()
@helpers.add_options(helpers.dry_option + mfilter.options)
@click.argument('destination')
@click.pass_context
def sync(ctx, dry, destination, **kwargs):
    '''Copy selected musics with filters to destination folder'''
    logger.info('Destination: %s', destination)
    mf = mfilter.Filter(**kwargs)
    musics = ctx.obj.u().do_filter(mf)

    files = lib.all_files(destination)
    destinations = {f[len(destination) + 1:]: f for f in files}
    sources = {m['path'][len(m['folder']) + 1:]: m['path'] for m in musics}
    to_delete = set(destinations.keys()) - set(sources.keys())
    if to_delete:
        with tqdm(total=len(to_delete), desc="Deleting music", disable=config.quiet) as pbar:
            for d in to_delete:
                if not dry:
                    try:
                        logger.info("Deleting %s", destinations[d])
                        os.remove(destinations[d])
                    except OSError as e:
                        logger.error(e)
                else:
                    logger.info("[DRY-RUN] False Deleting %s", destinations[d])
                pbar.update(1)
    to_copy = set(sources.keys()) - set(destinations.keys())
    if to_copy:
        with tqdm(total=len(to_copy), desc="Copying music", disable=config.quiet) as pbar:
            from shutil import copyfile
            for c in sorted(to_copy):
                final_destination = os.path.join(destination, c)
                if not dry:
                    logger.info("Copying %s to %s", sources[c], final_destination)
                    os.makedirs(os.path.dirname(final_destination), exist_ok=True)
                    copyfile(sources[c], final_destination)
                else:
                    logger.info("[DRY-RUN] False Copying %s to %s", sources[c], final_destination)
                pbar.update(1)

    import shutil
    for d in lib.empty_dirs(destination):
        if not dry:
            shutil.rmtree(d)
        logger.info("[DRY-RUN] Removing empty dir %s", d)


@cli.command()
@click.pass_context
@click.argument('folders', nargs=-1)
def consistency(ctx, folders):
    '''Check music files consistency'''
    if not folders:
        folders = ctx.obj.u().folders

    musics = helpers.genfiles(folders)
    pt = PrettyTable()
    pt.field_names = ["Inconsistency", "File"]
    for m in musics:
        try:
            if m.path.endswith('.flac'):
                if m.comment and not m.description:
                    pt.add_row(['Comment (' + m.comment + ') used in flac', m.path])
            if m.path.endswith('.mp3'):
                if m.description and not m.comment:
                    pt.add_row(['Description (' + m.description + ') used in mp3 : ', m.path])
            if not m.title:
                pt.add_row(["No title  : '" + m.title + "' on ", m.path])
            filename = os.path.basename(m.path)
            if filename == "{} - {}.mp3".format(str(m.number).zfill(2), m.title):
                continue
            if filename == "{} - {}.flac".format(str(m.number).zfill(2), m.title):
                continue
            pt.add_row(["Invalid title format, '{}' should start by '{}'". format(filename, '{} - {}'.format(str(m.number).zfill(2), m.title)), m.path])
            if m.artist not in m.path:
                pt.add_row(["Artist invalid : " + m.artist + " is not in ", m.path])
            if m.genre == '':
                pt.add_row(["No genre : ", m.path])
            if m.album == '':
                pt.add_row(["No album : ", m.path])
            if m.artist == '':
                pt.add_row(["No artist : ", m.path])
            if m.rating == 0.0:
                pt.add_row(["No rating : ", m.path])
            if m.number == -1:
                pt.add_row(["Invalid track number : ", m.path])
        except OSError:
            pt.add_row(["Could not open file : ", m.path])
    print(pt)


@cli.command(short_help='Music player')
@helpers.add_options(user.auth_options)
@helpers.add_options(mfilter.options)
@click.pass_context
def play(ctx, email, password, token, graphql, **kwargs):
    try:
        ctx.obj.u = lambda: user.User.new(email=email, password=password, token=token, graphql=graphql)
        mf = mfilter.Filter(**kwargs)
        p = ctx.obj.u().do_filter(mf)
        if not p:
            logger.warning('Empty playlist')
            return
        instance = vlc.Instance()
        songs = [song['path'] for song in p]
        player = instance.media_list_player_new()
        media_list = instance.media_list_new(songs)
        player.set_media_list(media_list)
        bindings = KeyBindings()

        @bindings.add('p')
        def _play_binding():
            def play():
                """Play song"""
                player.play()
            run_in_terminal(play)

        @bindings.add('q')
        def _quit_binding(event):
            player.pause()
            event.app.exit()

        @bindings.add('s')
        def _pause_binding():
            player.pause()

        @bindings.add('l')
        def _playlist_binding():
            def playlist():
                """List songs"""
                media_player = player.get_media_player()
                media = media_player.get_media()
                media.parse()
                artist = media.get_meta(vlc.Meta.Artist)
                album = media.get_meta(vlc.Meta.Album)
                title = media.get_meta(vlc.Meta.Title)
                for s in p:
                    if s['artist'] == artist and s['title'] == title and s['album'] == album:
                        print_formatted_text('> {}'.format(s['path']))
                    else:
                        print_formatted_text(s['path'])
                print_formatted_text('------------------------------------------')
            run_in_terminal(playlist)

        @bindings.add('right')
        def _next_binding():
            player.next()

        @bindings.add('left')
        def _previous_binding():
            player.previous()

        def bottom_toolbar():
            media_player = player.get_media_player()
            media = media_player.get_media()
            media.parse()
            media_time = lib.seconds_to_human(round(media_player.get_time() / 1000))
            media_length = lib.seconds_to_human(round(media_player.get_length() / 1000))
            artist = media.get_meta(vlc.Meta.Artist)
            album = media.get_meta(vlc.Meta.Album)
            title = media.get_meta(vlc.Meta.Title)
            current = '({} / {}) {} - {} - {}'.format(media_time, media_length, artist, album, title)
            get_app().invalidate()
            return HTML('Current song: {}'.format(current))

        player.play()
        print_formatted_text(HTML('Bindings: q = quit | p = play | s = pause/continue | right = next song | left = previous song | l = playlist'))

        root_container = HSplit(
            [Window(FormattedTextControl(lambda: bottom_toolbar, style='class:bottom-toolbar.text'), style='class:bottom-toolbar')]
        )
        layout = Layout(root_container)
        app = Application(layout=layout, key_bindings=bindings)
        app.run()
    except NameError:
        logger.critical("Your VLC version may be outdated: %s", vlc.libvlc_get_version())


@cli.command()
@click.pass_context
@helpers.add_options(helpers.dry_option + mfilter.options)
@click.argument('path', type=click.File('w'), default='-')
def playlist(ctx, path, dry, **kwargs):
    '''Generate a new playlist'''
    mf = mfilter.Filter(**kwargs)
    p = ctx.obj.u().playlist(mf)
    if not dry:
        print(p, file=path)
    else:
        logger.info('DRY RUN: Writing playlist to %s with content:\n%s', path, p)


@cli.command()
@click.pass_context
@helpers.add_options(helpers.dry_option + mfilter.options)
@click.argument('path', type=click.Path(exists=True))
@click.option('--prefix', envvar='MB_PREFIX', help="Append prefix before each path (implies relative)", default='')
@click.option('--suffix', envvar='MB_SUFFIX', help="Append this suffix to playlist name", default='')
def bests(ctx, dry, path, prefix, suffix, **kwargs):
    '''Generate bests playlists with some rules'''
    mf = mfilter.Filter(**kwargs)
    if prefix:
        ctx.obj.mf.relative = True
    playlists = ctx.obj.u().bests(mf)
    print(playlists)
    with tqdm(total=len(playlists), desc="Bests playlists", disable=config.quiet) as pbar:
        for p in playlists:
            playlist_filepath = os.path.join(path, p['name'] + suffix + '.m3u')
            content = indent(p['content'], prefix, lambda line: line != '#EXTM3U')
            if not dry:
                try:
                    with codecs.open(playlist_filepath, 'w', "utf-8-sig") as playlist_file:
                        logger.debug('Writing playlist to %s with content:\n%s', playlist_filepath, content)
                        playlist_file.write(content)
                except (LookupError, ValueError, UnicodeError) as e:
                    logger.info('Unable to write playlist to %s because of %s', playlist_filepath, e)
            else:
                logger.info('DRY RUN: Writing playlist to %s with content:\n%s', playlist_filepath, content)
            pbar.update(1)


@cli.command()
@click.argument('path')
@helpers.add_options(acoustid_apikey_option)
def fingerprint(path, acoustid_apikey):
    '''Print music fingerprint'''
    f = File(path)
    print(f.fingerprint(acoustid_apikey))
