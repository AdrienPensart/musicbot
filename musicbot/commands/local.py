import logging
import os
import codecs
import csv
import json
import datetime
from shutil import copyfile
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
from musicbot import helpers, user, lib
from musicbot.music import mfilter
from musicbot.config import config
from musicbot.music.file import supported_formats


logger = logging.getLogger(__name__)
logging.getLogger("vlc").setLevel(logging.NOTSET)


@click.group(help='''Local music management''', cls=helpers.GroupWithHelp)
def cli():
    pass


@cli.command(help='''List artists''')
@helpers.add_options(user.auth_options + helpers.output_option)
def artists(user, output):
    if output == 'table':
        pt = PrettyTable()
        pt.field_names = ["Name"]
        for a in user.artists:
            pt.add_row([a['name']])
        print(pt)
    elif output == 'json':
        print(json.dumps(user.artists))
    else:
        raise NotImplementedError


@cli.command(help='''Raw query''')
@click.argument('query')
@helpers.add_options(user.auth_options)
def execute(user, query):
    print(json.dumps(user._post(query)['data']))


@cli.command()
@helpers.add_options(user.auth_options)
def load_filters(user):
    '''Load default filters'''
    user.load_default_filters()


@cli.command(help='''List filters''')
@helpers.add_options(user.auth_options + helpers.output_option)
def filters(user, output):
    if output == 'json':
        print(json.dumps(user.filters))
    elif output == 'table':
        pt = PrettyTable()
        pt.field_names = ["Name", "Keywords", "No keywords", "Min rating", "Max rating"]
        for f in user.filters:
            pt.add_row([f['name'], f['keywords'], f['noKeywords'], f['minRating'], f['maxRating']])
        print(pt)
    else:
        raise NotImplementedError


@cli.command('filter', help='''Print a filter''')
@helpers.add_options(user.auth_options + helpers.output_option)
@click.argument('name')
def _filter(user, name, output):
    f = user.filter(name)
    if output == 'json':
        print(json.dumps(f))
    elif output == 'table':
        print(f)
    else:
        raise NotImplementedError


@cli.command(help='''Generate some stats for music collection with filters''')
@helpers.add_options(user.auth_options + helpers.output_option + mfilter.options)
def stats(user, output, **kwargs):
    mf = mfilter.Filter(**kwargs)
    stats = user.do_stat(mf)
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
    else:
        raise NotImplementedError


@cli.command(help='''List folders''')
@helpers.add_options(user.auth_options + helpers.output_option)
def folders(user, output):
    _folders = user.folders
    if output == 'json':
        print(json.dumps(_folders))
    elif output == 'table':
        pt = PrettyTable()
        pt.field_names = ["Folder"]
        for f in _folders:
            pt.add_row([f])
        print(pt)
    else:
        raise NotImplementedError


@cli.command(help='''(re)Load musics''')
@helpers.add_options(user.auth_options + helpers.folders_argument)
def scan(user, folders):
    if not folders:
        folders = user.folders
    files = helpers.genfiles(folders)
    user.bulk_insert(files)


@cli.command(help='''Just list music files''')
@helpers.add_options(user.auth_options + helpers.folders_argument)
def find(user, folders):
    if not folders:
        folders = user.folders

    files = lib.find_files(folders, supported_formats)
    for f in files:
        print(f[1])


@cli.command(help='''Watch files changes in folders''')
@helpers.add_options(user.auth_options)
def watch(user):
    user.watch()


@cli.command(help='''Clean all musics''')
@helpers.add_options(user.auth_options)
def clean(user):
    user.clean_musics()


@cli.command(help='''Copy selected musics with filters to destination folder''')
@helpers.add_options(user.auth_options + helpers.dry_option + mfilter.options)
@click.argument('destination')
def sync(user, dry, destination, **kwargs):
    logger.info('Destination: %s', destination)
    mf = mfilter.Filter(**kwargs)
    musics = user.do_filter(mf)

    files = list(lib.all_files(destination))
    logger.info(f"Files : {len(files)}")
    if not files:
        logger.warning("No files found in destination")

    destinations = {f[len(destination) + 1:]: f for f in files}
    logger.info(f"Destinations : {len(destinations)}")
    sources = {m['path'][len(m['folder']) + 1:]: m['path'] for m in musics}
    logger.info(f"Sources : {len(sources)}")
    to_delete = set(destinations.keys()) - set(sources.keys())
    logger.info(f"To delete: {len(to_delete)}")
    if to_delete:
        with tqdm(total=len(to_delete), disable=config.quiet) as pbar:
            for d in to_delete:
                pbar.set_description(f"Deleting musics and playlists: {os.path.basename(destinations[d])}")
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
    logger.info(f"To copy: {len(to_copy)}")
    if to_copy:
        with tqdm(total=len(to_copy), disable=config.quiet) as pbar:
            for c in sorted(to_copy):
                final_destination = os.path.join(destination, c)
                try:
                    pbar.set_description(f'Copying {os.path.basename(sources[c])} to {destination}')
                    if not dry:
                        logger.info("Copying %s to %s", sources[c], final_destination)
                        os.makedirs(os.path.dirname(final_destination), exist_ok=True)
                        copyfile(sources[c], final_destination)
                    else:
                        logger.info("[DRY-RUN] False Copying %s to %s", sources[c], final_destination)
                    pbar.update(1)
                except KeyboardInterrupt:
                    logger.debug(f"Cleanup {final_destination}")
                    os.remove(final_destination)
                    raise

    import shutil
    for d in lib.empty_dirs(destination):
        if any(e in d for e in lib.exceptions):
            logger.debug(f"Invalid path {d}")
            continue
        if not dry:
            shutil.rmtree(d)
        logger.info("[DRY-RUN] Removing empty dir %s", d)


@cli.command(help='''Check music files consistency''')
@helpers.add_options(user.auth_options + helpers.folders_argument)
def consistency(user, folders):
    if not folders:
        folders = user.folders

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
            if filename == f"{str(m.number).zfill(2)} - {m.title}.mp3":
                continue
            if filename == f"{str(m.number).zfill(2)} - {m.title}.flac":
                continue
            pt.add_row([f"Invalid title format, '{filename}' should start by '{str(m.number).zfill(2)} - {m.title}'", m.path])
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


@cli.command(help='''Generate a new playlist''')
@helpers.add_options(user.auth_options + helpers.dry_option + mfilter.options + helpers.output_option)
@click.argument('path', type=click.File('w'), default='-')
def playlist(user, output, path, dry, **kwargs):
    mf = mfilter.Filter(**kwargs)
    if output == 'm3u':
        p = user.playlist(mf)
        if not dry:
            print(p, file=path)
        else:
            logger.info('DRY RUN: Writing playlist to %s with content:\n%s', path, p)
    else:
        tracks = user.do_filter(mf)
        if output == 'json':
            print(json.dumps(tracks), file=path)
        elif output == 'table':
            pt = PrettyTable()
            pt.field_names = [
                "Title",
                "Album",
                "Artist",
            ]
            for t in tracks:
                pt.add_row([t['title'], t['album'], t['artist']])
            print(pt, file=path)
        elif output == 'csv':
            folders = user.folders
            logger.info('Scanning folders: %s', folders)
            files = helpers.genfiles(folders)

            musicwriter = csv.writer(path, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for f in files:
                musicwriter.writerow(f.ordered_dict().values())


@cli.command(help='''Generate bests playlists with some rules''')
@helpers.add_options(user.auth_options + helpers.dry_option + mfilter.options)
@click.argument('path', type=click.Path(exists=True))
@click.option('--prefix', envvar='MB_PREFIX', help="Append prefix before each path (implies relative)", default='')
@click.option('--suffix', envvar='MB_SUFFIX', help="Append this suffix to playlist name", default='')
def bests(user, dry, path, prefix, suffix, **kwargs):
    if prefix:
        kwargs['relative'] = True
    mf = mfilter.Filter(**kwargs)
    playlists = user.bests(mf)
    with tqdm(total=len(playlists), disable=config.quiet) as pbar:
        for p in playlists:
            playlist_filepath = os.path.join(path, p['name'] + suffix + '.m3u')
            pbar.set_description(f"Best playlist {prefix} {suffix}: {os.path.basename(playlist_filepath)}")
            content = indent(p['content'], prefix, lambda line: line != '#EXTM3U')
            if not dry:
                try:
                    with codecs.open(playlist_filepath, 'w', "utf-8-sig") as playlist_file:
                        logger.debug('Writing playlist to %s with content:\n%s', playlist_filepath, content)
                        playlist_file.write(content)
                except (FileNotFoundError, LookupError, ValueError, UnicodeError) as e:
                    logger.warning(f'Unable to write playlist to {playlist_filepath} because of {e}')
            else:
                logger.info('DRY RUN: Writing playlist to %s with content:\n%s', playlist_filepath, content)
            pbar.update(1)


@cli.command(help='Music player')
@helpers.add_options(user.auth_options + mfilter.options)
def play(user, **kwargs):
    try:
        mf = mfilter.Filter(**kwargs)
        p = user.do_filter(mf)
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
                        print_formatted_text(f'''> {s['path']}''')
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
            current = f'({media_time} / {media_length}) {artist} - {album} - {title}'
            get_app().invalidate()
            return HTML(f'Current song: {current}')

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
