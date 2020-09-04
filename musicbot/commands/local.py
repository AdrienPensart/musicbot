import logging
import io
import sys
import shutil
import os
import codecs
import json
import datetime
from shutil import copyfile
from textwrap import indent
import click
import enlighten
import attr
from prettytable import PrettyTable
from mutagen import MutagenError
from click_skeleton import AdvancedGroup, add_options

from musicbot import helpers, user
from musicbot.music import mfilter
from musicbot.player import play
from musicbot.playlist import print_playlist
from musicbot.config import config
from musicbot.music.file import File, checks_options, folder_argument
from musicbot.music.helpers import bytes_to_human, all_files, empty_dirs, except_directories


logger = logging.getLogger(__name__)


@click.group(help='''Local music management''', cls=AdvancedGroup)
def cli():
    pass


@cli.command(help='Count musics')
@add_options(user.auth_options)
def count(user):
    query = '''
    {
        rawMusics
        {
            totalCount
        }
    }
    '''
    print(json.dumps(user.post(query)['data']['rawMusics']['totalCount']))


@cli.command(help='Raw query')
@click.argument('query')
@add_options(user.auth_options)
def execute(user, query):
    print(json.dumps(user.post(query)['data']))


@cli.command(help='Load default filters')
@add_options(user.auth_options)
def load_filters(user):
    user.load_default_filters()


@cli.command(help='List filters')
@add_options(
    helpers.output_option +
    user.auth_options
)
def filters(user, output):
    if output == 'json':
        print(json.dumps(user.filters))
    elif output == 'table':
        pt = PrettyTable()
        pt.field_names = ["Name", "Keywords", "No keywords", "Min rating", "Max rating"]
        for f in user.filters:
            pt.add_row([f['name'], f['keywords'], f['noKeywords'], f['minRating'], f['maxRating']])
        print(pt)


@cli.command('filter', help='Print a filter')
@add_options(
    helpers.output_option +
    user.auth_options
)
@click.argument('name')
def _filter(user, name, output):
    f = user.filter(name)
    if output == 'json':
        print(json.dumps(f))
    elif output == 'table':
        print(f)


@cli.command(aliases=['stat'], help='Generate some stats for music collection with filters')
@add_options(
    helpers.output_option +
    user.auth_options +
    mfilter.mfilter_options
)
def stats(user, output, music_filter):
    stats = user.do_stat(music_filter)
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
        pt.add_row(["Size", bytes_to_human(int(stats['size']))])
        pt.add_row(["Total duration", datetime.timedelta(seconds=int(stats['duration']))])
        print(pt)


@cli.command(help='List folders')
@add_options(
    helpers.output_option +
    user.auth_options
)
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


@cli.command(help='(re)Load musics')
@add_options(
    helpers.folders_argument +
    user.auth_options
)
def scan(user, folders):
    if not folders:
        folders = user.folders
    files = helpers.genfiles(folders)
    user.bulk_insert(files)


@cli.command(help='Watch files changes in folders')
@add_options(user.auth_options)
def watch(user):
    user.watch()


@cli.command(help='Clean all musics')
@add_options(user.auth_options)
def clean(user):
    user.clean_musics()


@cli.command(help='Copy selected musics with filters to destination folder')
@add_options(
    helpers.dry_option +
    user.auth_options +
    mfilter.mfilter_options
)
@click.argument('destination')
def sync(user, dry, destination, music_filter):
    logger.info(f'Destination: {destination}')
    musics = user.do_filter(music_filter)

    files = list(all_files(destination))
    logger.info(f"Files : {len(files)}")
    if not files:
        logger.warning("No files found in destination")

    destinations = {f[len(destination) + 1:]: f for f in files}
    logger.info(f"Destinations : {len(destinations)}")
    sources = {m['path'][len(m['folder']) + 1:]: m['path'] for m in musics}
    logger.info(f"Sources : {len(sources)}")
    to_delete = set(destinations.keys()) - set(sources.keys())
    with enlighten.Manager(stream=sys.stderr) as manager:
        logger.info(f"To delete: {len(to_delete)}")
        enabled = to_delete and not config.quiet
        with manager.counter(total=len(to_delete), enabled=enabled) as pbar:
            for d in to_delete:
                try:
                    pbar.desc = f"Deleting musics and playlists: {os.path.basename(destinations[d])}"
                    if not dry:
                        try:
                            logger.info(f"Deleting {destinations[d]}")
                            os.remove(destinations[d])
                        except OSError as e:
                            logger.error(e)
                    else:
                        logger.info(f"[DRY-RUN] False Deleting {destinations[d]}")
                finally:
                    pbar.update()

        to_copy = set(sources.keys()) - set(destinations.keys())
        logger.info(f"To copy: {len(to_copy)}")
        enabled = to_copy and not config.quiet
        with manager.counter(total=len(to_copy), enabled=enabled) as pbar:
            for c in sorted(to_copy):
                final_destination = os.path.join(destination, c)
                try:
                    pbar.desc = f'Copying {os.path.basename(sources[c])} to {destination}'
                    if not dry:
                        logger.info(f"Copying {sources[c]} to {final_destination}")
                        os.makedirs(os.path.dirname(final_destination), exist_ok=True)
                        copyfile(sources[c], final_destination)
                    else:
                        logger.info(f"[DRY-RUN] False Copying {sources[c]} to {final_destination}")
                except KeyboardInterrupt:
                    logger.debug(f"Cleanup {final_destination}")
                    try:
                        os.remove(final_destination)
                    except OSError:
                        pass
                    raise
                finally:
                    pbar.update()

    for d in empty_dirs(destination):
        if any(e in d for e in except_directories):
            logger.debug(f"Invalid path {d}")
            continue
        if not dry:
            shutil.rmtree(d)
        logger.info(f"[DRY-RUN] Removing empty dir {d}")


@cli.command(help='Generate a new playlist')
@add_options(
    helpers.dry_option +
    helpers.playlist_output_option +
    user.auth_options +
    mfilter.mfilter_options
)
@click.argument('path', type=click.File('w'), default='-')
def playlist(user, output, path, dry, music_filter):
    if output == 'm3u':
        p = user.playlist(music_filter)
        if not dry:
            print(p, file=path)
        else:
            logger.info(f'DRY RUN: Writing playlist to {path} with content:\n{p}')
    elif output == 'json':
        tracks = user.do_filter(music_filter)
        print(json.dumps(tracks), file=path)
    elif output == 'table':
        tracks = user.do_filter(music_filter)
        print_playlist(tracks, path)


@cli.command(help='Generate bests playlists with some rules')
@click.option('--prefix', envvar='MB_PREFIX', help="Append prefix before each path (implies relative)", default='')
@click.option('--suffix', envvar='MB_SUFFIX', help="Append this suffix to playlist name", default='')
@add_options(
    folder_argument +
    helpers.dry_option +
    user.auth_options +
    mfilter.mfilter_options
)
def bests(user, dry, folder, prefix, suffix, music_filter):
    if prefix:
        music_filter = attr.evolve(music_filter, relative=True)
        if not prefix.endswith('/'):
            prefix += '/'
    playlists = user.bests(music_filter)
    enabled = playlists and not config.quiet
    with enlighten.Manager(stream=sys.stderr, enabled=enabled) as manager:
        with manager.counter(total=len(playlists)) as pbar:
            for p in playlists:
                try:
                    playlist_filepath = os.path.join(folder, p['name'] + suffix + '.m3u')
                    pbar.desc = f"Best playlist {prefix} {suffix}: {os.path.basename(playlist_filepath)}"
                    content = indent(p['content'], prefix, lambda line: line != '#EXTM3U\n')
                    if not dry:
                        try:
                            with codecs.open(playlist_filepath, 'w', "utf-8-sig") as playlist_file:
                                logger.debug(f'Writing playlist to {playlist_filepath} with content:\n{content}')
                                playlist_file.write(content)
                        except (OSError, LookupError, ValueError, UnicodeError) as e:
                            logger.warning(f'Unable to write playlist to {playlist_filepath} because of {e}')
                    else:
                        logger.info(f'DRY RUN: Writing playlist to {playlist_filepath} with content:\n{content}')
                finally:
                    pbar.update()


@cli.command(aliases=['play'], help='Music player')
@add_options(
    user.auth_options +
    mfilter.mfilter_options
)
def player(user, music_filter):
    try:
        tracks = user.do_filter(music_filter)
        play(tracks)
    except io.UnsupportedOperation:
        logger.critical('Unable to load UI')


@cli.command(aliases=['consistency'], help='Check music consistency')
@add_options(
    checks_options +
    helpers.dry_option +
    user.auth_options +
    mfilter.mfilter_options
)
def inconsistencies(user, dry, fix, checks, music_filter):
    tracks = user.do_filter(music_filter)
    pt = PrettyTable()
    pt.field_names = ["Folder", "Path", "Inconsistencies"]
    for t in tracks:
        try:
            m = File(t['path'], t['folder'])
            if fix:
                m.fix(dry=dry, checks=checks)
            if m.inconsistencies:
                pt.add_row([m.folder, m.path, ', '.join(m.inconsistencies)])
        except (OSError, MutagenError):
            pt.add_row([t['folder'], t['path'], "could not open file"])
    print(pt)
