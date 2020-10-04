import logging
import io
import random
import shutil
import os
import itertools
import codecs
import json
import datetime
import textwrap
import click
import attr
import mutagen  # type: ignore
from prettytable import PrettyTable  # type: ignore
from click_skeleton import AdvancedGroup, add_options
from click_skeleton.helpers import PrettyDefaultDict

from musicbot import helpers, user_options
from musicbot.player import play
from musicbot.playlist import print_playlist
from musicbot.config import config
from musicbot.music import music_filter_options
from musicbot.music.file import File, flat_option, checks_options, folder_argument
from musicbot.music.helpers import bytes_to_human, all_files, empty_dirs, except_directories


logger = logging.getLogger(__name__)


@click.group('local', help='Local music management', cls=AdvancedGroup)
def cli() -> None:
    pass


@cli.command(help='Count musics')
@add_options(user_options.auth_options)
def count(user):
    print(user.count_musics())


@cli.command(help='Raw query', aliases=['query', 'fetch'])
@click.argument('query')
@add_options(user_options.auth_options)
def execute(user, query):
    print(json.dumps(user.fetch(query)))


@cli.command(aliases=['stat'], help='Generate some stats for music collection with filters')
@add_options(
    helpers.output_option,
    user_options.auth_options,
    music_filter_options.options,
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
    helpers.output_option,
    user_options.auth_options,
)
def folders(user, output):
    _folders = user.folders()
    if output == 'json':
        print(json.dumps(_folders))
    elif output == 'table':
        pt = PrettyTable()
        pt.field_names = ["Folder"]
        for f in _folders:
            pt.add_row([f])
        print(pt)


@cli.command(help='Load musics')
@add_options(
    helpers.folders_argument,
    user_options.auth_options,
)
def scan(user, folders):
    if not folders:
        folders = user.folders()
    files = helpers.genfiles(folders)
    user.bulk_insert(files)


@cli.command(help='Watch files changes in folders')
@add_options(user_options.auth_options)
def watch(user):
    user.watch()


@cli.command(help='Clean all musics')
@add_options(
    user_options.auth_options,
    helpers.yes_option,
)
def clean(user, yes):
    if yes or click.confirm("Are you sure to delete all musics from DB?"):
        user.clean_musics()


@cli.command(help='Clean and load musics')
@add_options(
    helpers.folders_argument,
    user_options.auth_options,
)
def rescan(user, folders):
    if not folders:
        folders = user.folders()
    files = helpers.genfiles(folders)
    user.clean_musics()
    user.bulk_insert(files)


@cli.command(help='Copy selected musics with filters to destination folder')
@add_options(
    helpers.dry_option,
    helpers.yes_option,
    user_options.auth_options,
    music_filter_options.options,
    flat_option,
)
@click.option('--delete', help='Delete files on destination if not present in library', is_flag=True)
@click.argument('destination')
def sync(user, delete, yes, dry, destination, music_filter, flat):
    logger.info(f'Destination: {destination}')
    musics = user.do_filter(music_filter)
    if not musics:
        click.secho('no result for filter, nothing to sync')
        return

    music_files = [File(path=m['path'], folder=m['folder']) for m in musics]

    files = list(all_files(destination))
    logger.info(f"Files : {len(files)}")
    if not files:
        logger.warning("no files found in destination")

    destinations = {f[len(destination) + 1:]: f for f in files}

    logger.info(f"Destinations : {len(destinations)}")
    if flat:
        sources = {m.flat_filename: m.path for m in music_files}
    else:
        sources = {m.filename: m.path for m in music_files}

    logger.info(f"Sources : {len(sources)}")
    to_delete = set(destinations.keys()) - set(sources.keys())
    if delete and (yes or click.confirm(f'Do you really want to delete {len(to_delete)} files and playlists ?')):
        with config.progressbar(max_value=len(to_delete)) as pbar:
            for d in to_delete:
                try:
                    pbar.desc = f"Deleting musics and playlists: {os.path.basename(destinations[d])}"
                    if dry:
                        logger.info(f"[DRY-RUN] Deleting {destinations[d]}")
                        continue
                    try:
                        logger.info(f"Deleting {destinations[d]}")
                        os.remove(destinations[d])
                    except OSError as e:
                        logger.error(e)
                finally:
                    pbar.value += 1
                    pbar.update()

    to_copy = set(sources.keys()) - set(destinations.keys())
    with config.progressbar(max_value=len(to_copy)) as pbar:
        logger.info(f"To copy: {len(to_copy)}")
        for c in sorted(to_copy):
            final_destination = os.path.join(destination, c)
            try:
                pbar.desc = f'Copying {os.path.basename(sources[c])} to {destination}'
                if dry:
                    logger.info(f"[DRY-RUN] Copying {sources[c]} to {final_destination}")
                    continue
                logger.info(f"Copying {sources[c]} to {final_destination}")
                os.makedirs(os.path.dirname(final_destination), exist_ok=True)
                shutil.copyfile(sources[c], final_destination)
            except KeyboardInterrupt:
                logger.debug(f"Cleanup {final_destination}")
                try:
                    os.remove(final_destination)
                except OSError:
                    pass
                raise
            finally:
                pbar.value += 1
                pbar.update()

    for d in empty_dirs(destination):
        if any(e in d for e in except_directories):
            logger.debug(f"Invalid path {d}")
            continue
        if not dry:
            shutil.rmtree(d)
        logger.info(f"[DRY-RUN] Removing empty dir {d}")


@cli.command(help='Generate a new playlist')
@click.option('--interleave', help='Interleave tracks by artist', is_flag=True)
@add_options(
    helpers.dry_option,
    helpers.playlist_output_option,
    user_options.auth_options,
    music_filter_options.options,
)
@click.argument('path', type=click.File('w'), default='-')
def playlist(user, output, path, dry, music_filter, interleave):
    tracks = user.do_filter(music_filter)

    if interleave:
        tracks_by_artist = PrettyDefaultDict(list)
        for track in tracks:
            tracks_by_artist[track['artist']].append(track)
        tracks = [
            track
            for track in itertools.chain(*itertools.zip_longest(*tracks_by_artist.values()))
            if track is not None
        ]
        if music_filter.shuffle:
            random.shuffle(tracks)

    if output == 'm3u':
        p = '#EXTM3U\n'
        p += '\n'.join([track['path'] for track in tracks])
        if not dry:
            print(p, file=path)
    elif output == 'json':
        print(json.dumps(tracks), file=path)
    elif output == 'table':
        print_playlist(tracks, path)


@cli.command(help='Generate bests playlists with some rules')
@click.option('--prefix', envvar='MB_PREFIX', help="Append prefix before each path (implies relative)", default='')
@click.option('--suffix', envvar='MB_SUFFIX', help="Append this suffix to playlist name", default='')
@add_options(
    folder_argument,
    helpers.dry_option,
    user_options.auth_options,
    music_filter_options.options,
)
def bests(user, dry, folder, prefix, suffix, music_filter):
    if prefix:
        music_filter = attr.evolve(music_filter, relative=True)
        if not prefix.endswith('/'):
            prefix += '/'
    playlists = user.bests(music_filter)
    with config.progressbar(max_value=len(playlists)) as pbar:
        for p in playlists:
            try:
                playlist_filepath = os.path.join(folder, p['name'] + suffix + '.m3u')
                content = textwrap.indent(p['content'], prefix, lambda line: line != '#EXTM3U\n')
                if dry:
                    logger.info(f'DRY RUN: Writing playlist to {playlist_filepath} with content:\n{content}')
                    continue
                try:
                    with codecs.open(playlist_filepath, 'w', "utf-8-sig") as playlist_file:
                        logger.debug(f'Writing playlist to {playlist_filepath} with content:\n{content}')
                        playlist_file.write(content)
                except (OSError, LookupError, ValueError, UnicodeError) as e:
                    logger.warning(f'Unable to write playlist to {playlist_filepath} because of {e}')
            finally:
                pbar.value += 1
                pbar.update()


@cli.command(aliases=['play'], help='Music player')
@add_options(
    user_options.auth_options,
    music_filter_options.options,
)
def player(user, music_filter):
    try:
        tracks = user.do_filter(music_filter)
        play(tracks)
    except io.UnsupportedOperation:
        logger.critical('Unable to load UI')


@cli.command(aliases=['consistency'], help='Check music consistency')
@add_options(
    checks_options,
    helpers.dry_option,
    user_options.auth_options,
    music_filter_options.options,
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
        except (OSError, mutagen.MutagenError):
            pt.add_row([t['folder'], t['path'], "could not open file"])
    print(pt)
