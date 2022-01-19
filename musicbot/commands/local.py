from typing import Tuple, List
from pathlib import Path
import logging
import time
import io
import random
import shutil
import codecs
import json
import datetime
import textwrap
import click
import progressbar  # type: ignore
import mutagen  # type: ignore
from beartype import beartype
from watchdog.observers import Observer  # type: ignore
from prettytable import PrettyTable  # type: ignore
from click_skeleton import AdvancedGroup
from musicbot.cli.file import extensions_option, link_options, flat_option, checks_and_fix_options
from musicbot.cli.folders import destination_argument, folders_argument, folder_argument
from musicbot.cli.music_filter import music_filter_options
from musicbot.cli.user import user_options
from musicbot.cli.options import yes_option, save_option, output_option, dry_option, clean_option

from musicbot.watcher import MusicWatcherHandler
from musicbot.player import play
from musicbot.object import MusicbotObject
from musicbot.user import User
from musicbot.music.music_filter import MusicFilter
from musicbot.music.file import File
from musicbot.music.folders import Folders, except_directories


logger = logging.getLogger(__name__)


@click.group('local', help='Local music management', cls=AdvancedGroup)
@beartype
def cli() -> None:
    pass


@cli.command(help='Count musics')
@user_options
@beartype
def count(user: User) -> None:
    print(user.count_musics())


@cli.command(help='Raw query', aliases=['query', 'fetch'])
@click.argument('query')
@user_options
@beartype
def execute(user: User, query: str) -> None:
    print(json.dumps(user.fetch(query)))


@cli.command(aliases=['stat'], help='Generate some stats for music collection with filters')
@output_option
@user_options
@music_filter_options
@beartype
def stats(user: User, output: str, music_filter: MusicFilter) -> None:
    stats = user.do_stat(music_filter)
    if output == 'json':
        print(json.dumps(stats))
    elif output == 'table':
        pt = PrettyTable(["Stat", "Value"])
        pt.add_row(["Music", stats['musics']])
        pt.add_row(["Link", stats['links']])
        pt.add_row(["Artist", stats['artists']])
        pt.add_row(["Album", stats['albums']])
        pt.add_row(["Genre", stats['genres']])
        pt.add_row(["Keywords", stats['keywords']])
        pt.add_row(["Total duration", datetime.timedelta(seconds=int(stats['duration']))])
        print(pt)


@cli.command(help='Load musics')
@folders_argument
@extensions_option
@save_option
@clean_option
@link_options
@user_options
@beartype
def scan(
    user: User,
    clean: bool,
    save: bool,
    folders: Tuple[Path, ...],
    extensions: Tuple[str, ...],
    http: bool,
    sftp: bool,
    youtube: bool,
    spotify: bool,
    local: bool,
) -> None:
    if clean:
        user.clean_musics()

    musics = Folders(folders=folders, extensions=extensions).musics
    user.bulk_insert(
        musics,
        http=http,
        sftp=sftp,
        youtube=youtube,
        spotify=spotify,
        local=local,
    )

    if save:
        MusicbotObject.config.configfile['musicbot']['folders'] = ','.join({str(folder) for folder in folders})
        MusicbotObject.config.write()


@cli.command(help='Watch files changes in folders')
@folders_argument
@extensions_option
@user_options
@beartype
def watch(user: User, folders: Tuple[Path, ...], extensions: Tuple[str, ...]) -> None:
    event_handler = MusicWatcherHandler(user=user, folders=folders, extensions=extensions)
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
@beartype
def clean(user: User) -> None:
    user.clean_musics()


@cli.command('tracks', help='Generate a new playlist')
@user_options
@music_filter_options
@beartype
def _tracks(user: User, music_filter: MusicFilter) -> None:
    tracks = user.playlist(music_filter)
    print(json.dumps(tracks))


@cli.command(help='Generate a new playlist')
@output_option
@user_options
@link_options
@music_filter_options
@beartype
def playlist(output: str, user: User, music_filter: MusicFilter, http: bool, sftp: bool, youtube: bool, spotify: bool, local: bool) -> None:
    musics = user.playlist(music_filter)
    if music_filter.shuffle:
        random.shuffle(musics)

    urls = []
    pt = PrettyTable(['url'])
    pt.align = 'l'
    for music in musics:
        links = music['links']
        if not links:
            MusicbotObject.warn(f'{music} : no links available')
        for link in links:
            if 'youtube' in link:
                if youtube:
                    urls.append(link)
                    pt.add_row([link])
                continue

            if 'http' in link:
                if http:
                    urls.append(link)
                    pt.add_row([link])
                continue

            if 'spotify' in link:
                if spotify:
                    urls.append(link)
                    pt.add_row([link])
                continue

            if 'sftp' in link:
                if sftp:
                    urls.append(link)
                    pt.add_row([link])
                continue

            if local:
                path = Path(link)
                if not path.exists():
                    MusicbotObject.warn(f'{link} does not exist locally, skipping')
                    continue
                urls.append(link)
                pt.add_row([link])

    if output == 'm3u':
        p = '#EXTM3U\n'
        p += '\n'.join(urls)
        print(p)
        return

    if output == 'table':
        print(pt)
        return

    if output == 'json':
        print(json.dumps(musics))
        return


@cli.command(help='Generate bests playlists with some rules')
@click.option('--prefix', envvar='MB_PREFIX', help="Append prefix before each path", default='')
@click.option('--suffix', envvar='MB_SUFFIX', help="Append this suffix to playlist name", default='')
@folder_argument
@dry_option
@user_options
@music_filter_options
@beartype
def bests(user: User, folder: Path, prefix: str, suffix: str, music_filter: MusicFilter) -> None:
    playlists = user.bests(music_filter)
    with MusicbotObject.progressbar(max_value=len(playlists)) as pbar:
        for p in playlists:
            try:
                playlist_filepath = Path(folder) / (p['name'] + suffix + '.m3u')
                content = textwrap.indent(p['content'], prefix, lambda line: line != '#EXTM3U\n')
                if MusicbotObject.dry:
                    logger.info(f'DRY RUN: Writing playlist to {playlist_filepath} with content:\n{content}')
                    continue
                try:
                    playlist_filepath.parent.mkdir(parents=True, exist_ok=True)
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
@beartype
def player(user: User, music_filter: MusicFilter) -> None:
    if not MusicbotObject.config.quiet:
        progressbar.streams.unwrap(stderr=True, stdout=True)
    try:
        tracks = user.playlist(music_filter)
        play(tracks)
    except io.UnsupportedOperation:
        logger.critical('Unable to load UI')


@cli.command(aliases=['consistency'], help='Check music consistency')
@checks_and_fix_options
@dry_option
@user_options
@music_filter_options
@beartype
def inconsistencies(user: User, fix: bool, checks: Tuple[str, ...], music_filter: MusicFilter) -> None:
    musics = user.playlist(music_filter)
    pt = PrettyTable(["Path", "Inconsistencies"])
    for music in musics:
        try:
            m = File(music['path'])
            if fix:
                m.fix(checks=checks)
            if m.inconsistencies:
                pt.add_row([m.path, ', '.join(m.inconsistencies)])
        except (OSError, mutagen.MutagenError):
            pt.add_row([music['path'], "could not open file"])
    print(pt)


@cli.command(help='Copy selected musics with filters to destination folder')
@destination_argument
@dry_option
@click.option('--yes', '-y', help="Confirm file deletion on destination", is_flag=True)
@user_options
@music_filter_options
@flat_option
@click.option('--delete', help='Delete files on destination if not present in library', is_flag=True)
@beartype
def sync(user: User, delete: bool, destination: Path, music_filter: MusicFilter, yes: bool, flat: bool) -> None:
    logger.info(f'Destination: {destination}')
    objs = user.playlist(music_filter)
    if not objs:
        click.secho('no result for filter, nothing to sync')
        return

    folders = Folders(folders=[destination], extensions=[])
    logger.info(f"Files : {len(folders.files)}")
    if not folders.files:
        logger.warning("no files found in destination")

    destinations = {str(file)[len(str(destination)) + 1:]: file for file in folders.files}

    musics: List[File] = []
    for obj in objs:
        for link in obj['links']:
            try:
                if link.startswith('ssh://'):
                    continue
                musics.append(File(path=Path(link)))
            except OSError as e:
                logger.error(e)

    logger.info(f"Destinations : {len(destinations)}")
    if flat:
        sources = {music.flat_filename: music.path for music in musics}
    else:
        sources = {music.filename: music.path for music in musics}

    logger.info(f"Sources : {len(sources)}")
    to_delete = set(destinations.keys()) - set(sources.keys())
    if delete and (yes or click.confirm(f'Do you really want to delete {len(to_delete)} files and playlists ?')):
        with MusicbotObject.progressbar(max_value=len(to_delete)) as pbar:
            for d in to_delete:
                try:
                    path_to_delete = Path(destinations[d])
                    pbar.desc = f"Deleting musics and playlists: {path_to_delete.name}"
                    if MusicbotObject.dry:
                        logger.info(f"[DRY-RUN] Deleting {path_to_delete}")
                        continue
                    try:
                        logger.info(f"Deleting {path_to_delete}")
                        path_to_delete.unlink()
                    except OSError as e:
                        logger.error(e)
                finally:
                    pbar.value += 1
                    pbar.update()

    to_copy = set(sources.keys()) - set(destinations.keys())
    with MusicbotObject.progressbar(max_value=len(to_copy)) as pbar:
        logger.info(f"To copy: {len(to_copy)}")
        for c in sorted(to_copy):
            final_destination = destination / c
            try:
                path_to_copy = Path(sources[c])
                pbar.desc = f'Copying {path_to_copy.name} to {destination}'
                if MusicbotObject.dry:
                    logger.info(f"[DRY-RUN] Copying {path_to_copy.name} to {final_destination}")
                    continue
                logger.info(f"Copying {path_to_copy.name} to {final_destination}")

                Path(final_destination).parent.mkdir(exist_ok=True)
                shutil.copyfile(path_to_copy, final_destination)
            except KeyboardInterrupt:
                logger.debug(f"Cleanup {final_destination}")
                try:
                    final_destination.unlink()
                except OSError:
                    pass
                raise
            finally:
                pbar.value += 1
                pbar.update()

    for d in folders.empty_dirs():
        if any(e in d for e in except_directories):
            logger.debug(f"Invalid path {d}")
            continue
        if not MusicbotObject.dry:
            shutil.rmtree(d)
        logger.info(f"[DRY-RUN] Removing empty dir {d}")
