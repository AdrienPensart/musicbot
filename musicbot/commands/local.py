from typing import List
import logging
import time
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
import progressbar  # type: ignore
import mutagen  # type: ignore
from watchdog.observers import Observer  # type: ignore
from prettytable import PrettyTable  # type: ignore
from click_skeleton import AdvancedGroup
from click_skeleton.helpers import PrettyDefaultDict
from musicbot.helpers import genfiles
from musicbot.exceptions import FailedRequest
from musicbot.watcher import MusicWatcherHandler
from musicbot.player import play
from musicbot.playlist import print_playlist
from musicbot.object import MusicbotObject
from musicbot.user import User
from musicbot.music.music_filter import MusicFilter
from musicbot.music.file import File
from musicbot.music.helpers import all_files, empty_dirs, except_directories
from musicbot.cli.file import flat_option, checks_and_fix_options, folder_argument
from musicbot.cli.music_filter import music_filter_options, interleave_option
from musicbot.cli.user import user_options
from musicbot.cli.options import yes_option, save_option, folders_argument, output_option, dry_option


logger = logging.getLogger(__name__)


@click.group('local', help='Local music management', cls=AdvancedGroup)
def cli() -> None:
    pass


@cli.command(help='Count musics')
@user_options
def count(user: User):
    print(user.count_musics())


@cli.command(help='Raw query', aliases=['query', 'fetch'])
@click.argument('query')
@user_options
def execute(user: User, query: str):
    print(json.dumps(user.fetch(query)))


@cli.command(aliases=['stat'], help='Generate some stats for music collection with filters')
@output_option
@user_options
@music_filter_options
def stats(user: User, output: str, music_filter: MusicFilter):
    stats = user.do_stat(music_filter)
    if output == 'json':
        print(json.dumps(stats))
    elif output == 'table':
        pt = PrettyTable(["Stat", "Value"])
        pt.add_row(["Music", stats['musics']])
        pt.add_row(["Artist", stats['artists']])
        pt.add_row(["Album", stats['albums']])
        pt.add_row(["Genre", stats['genres']])
        pt.add_row(["Keywords", stats['keywords']])
        pt.add_row(["Total duration", datetime.timedelta(seconds=int(stats['duration']))])
        print(pt)


@cli.command(help='Load musics')
@folders_argument
@save_option
@user_options
def scan(user: User, save: bool, folders: List[str]):
    files = genfiles(folders)

    try:
        user.bulk_insert(files)
    except FailedRequest as e:
        MusicbotObject.err(f"{folders} : {e}")

    if save:
        MusicbotObject.config.configfile['musicbot']['folders'] = ','.join(set(folders))
        MusicbotObject.config.write()


@cli.command(help='Watch files changes in folders')
@folders_argument
@user_options
def watch(user: User, folders: List[str]):
    event_handler = MusicWatcherHandler(user=user, folders=folders)
    observer = Observer()
    for folder in folders:
        observer.schedule(event_handler, folder, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(50)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


@cli.command(help='Clean all musics')
@user_options
@yes_option
def clean(user: User, yes: bool):
    if yes or click.confirm("Are you sure to delete all musics from DB?"):
        user.clean_musics()


@cli.command(help='Clean and load musics')
@folders_argument
@user_options
def rescan(user: User, folders: List[str]):
    files = genfiles(folders)
    user.clean_musics()
    user.bulk_insert(files)


@cli.command(help='Copy selected musics with filters to destination folder')
@dry_option
@yes_option
@user_options
@music_filter_options
@flat_option
@click.option('--delete', help='Delete files on destination if not present in library', is_flag=True)
@click.argument('destination')
def sync(user: User, delete: bool, yes: bool, dry: bool, destination: str, music_filter: MusicFilter, flat: bool):
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
        with MusicbotObject.progressbar(max_value=len(to_delete)) as pbar:
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
    with MusicbotObject.progressbar(max_value=len(to_copy)) as pbar:
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


@cli.command(help='Generate a new playlist', aliases=['tracks'])
@output_option
@user_options
@music_filter_options
@interleave_option
def playlist(user: User, output: str, music_filter: MusicFilter, interleave: bool):
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
        print(p)
        return

    if output == 'json':
        print(json.dumps(tracks))
        return

    if output == 'table':
        print_playlist(tracks)


@cli.command(help='Generate bests playlists with some rules')
@click.option('--prefix', envvar='MB_PREFIX', help="Append prefix before each path (implies relative)", default='')
@click.option('--suffix', envvar='MB_SUFFIX', help="Append this suffix to playlist name", default='')
@folder_argument
@dry_option
@user_options
@music_filter_options
def bests(user: User, dry: bool, folder: str, prefix: str, suffix: str, music_filter: MusicFilter):
    if prefix:
        music_filter = attr.evolve(music_filter, relative=True)
        if not prefix.endswith('/'):
            prefix += '/'
    playlists = user.bests(music_filter)
    with MusicbotObject.progressbar(max_value=len(playlists)) as pbar:
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
@user_options
@music_filter_options
def player(user: User, music_filter: MusicFilter):
    if not MusicbotObject.config.quiet:
        progressbar.streams.unwrap(stderr=True, stdout=True)
    try:
        tracks = user.do_filter(music_filter)
        play(tracks)
    except io.UnsupportedOperation:
        logger.critical('Unable to load UI')


@cli.command(aliases=['consistency'], help='Check music consistency')
@checks_and_fix_options
@dry_option
@user_options
@music_filter_options
def inconsistencies(user: User, dry: bool, fix: bool, checks: List[str], music_filter: MusicFilter):
    tracks = user.do_filter(music_filter)
    pt = PrettyTable(["Folder", "Path", "Inconsistencies"])
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
