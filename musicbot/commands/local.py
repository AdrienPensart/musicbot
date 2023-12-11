import asyncio
import logging
from dataclasses import asdict
from pathlib import Path

import click
import edgedb
from beartype import beartype
from click_skeleton import AdvancedGroup
from rich.table import Table
from watchfiles import Change, DefaultFilter, awatch

from musicbot import (
    File,
    MusicbotObject,
    MusicDb,
    MusicFilter,
    PlaylistOptions,
    ScanFolders,
    local,
    syncify,
)
from musicbot.cli.file import flat_option
from musicbot.cli.music_filter import FILTERS_REPRS, music_filters_options
from musicbot.cli.musicdb import musicdb_options
from musicbot.cli.options import (
    clean_option,
    coroutines_option,
    dry_option,
    lazy_yes_option,
    output_option,
    save_option,
    yes_option,
)
from musicbot.cli.playlist import bests_options, playlist_options
from musicbot.cli.scan_folders import (
    destination_argument,
    scan_folder_argument,
    scan_folders_argument,
)

logger = logging.getLogger(__name__)


@click.group("local", help="Local music management", cls=AdvancedGroup)
@beartype
def cli() -> None:
    pass


@cli.command(help="List folders and some stats")
@musicdb_options
@output_option
@syncify
@beartype
async def folders(musicdb: MusicDb, output: str) -> None:
    all_folders = await musicdb.folders()

    table = Table(
        "Name",
        "IPv4",
        "Size",
        "Length",
        "Genres",
        "Artists",
        "Albums",
        "Musics",
        "Keywords",
        title="Folders",
    )
    for folder in all_folders:
        table.add_row(
            folder.name,
            folder.ipv4,
            folder.human_size,
            folder.human_duration,
            str(folder.n_genres),
            str(folder.n_artists),
            str(folder.n_albums),
            str(folder.n_musics),
            str(folder.n_keywords),
        )
    table.caption = f"{len(all_folders)} listed"

    if output == "table":
        MusicbotObject.print_table(table)
    elif output == "json":
        MusicbotObject.print_json([asdict(folder) for folder in all_folders])


@cli.command(help="Remove one or more music", aliases=["delete"])
@click.argument("files", nargs=-1)
@musicdb_options
@syncify
@beartype
async def remove(
    files: tuple[str, ...],
    musicdb: MusicDb,
) -> None:
    for file in files:
        _ = await musicdb.remove_music_path(file)


@cli.command(help="Clean all musics", aliases=["wipe"])
@musicdb_options
@yes_option
@syncify
@beartype
async def clean(
    musicdb: MusicDb,
) -> None:
    _ = await musicdb.clean_musics()


@cli.command(help="Load musics")
@scan_folders_argument
@musicdb_options
@save_option
@output_option
@clean_option
@coroutines_option
@syncify
@beartype
async def scan(
    musicdb: MusicDb,
    scan_folders: ScanFolders,
    clean: bool,
    save: bool,
    output: str,
) -> None:
    music_inputs = await local.scan(
        musicdb=musicdb,
        scan_folders=scan_folders,
    )
    if clean:
        _ = await musicdb.clean_musics()
    music_outputs = await local.upsert_musics(
        musicdb=musicdb,
        music_inputs=music_inputs,
    )
    _ = await musicdb.soft_clean()

    if output == "json":
        MusicbotObject.print_json([asdict(mo) for mo in music_outputs])

    if save:
        MusicbotObject.config.configfile["musicbot"]["folders"] = scan_folders.unique_directories
        MusicbotObject.config.write()


@cli.command(help="Watch files changes in folders", aliases=["watcher"])
@scan_folders_argument
@musicdb_options
@click.option("--sleep", help="Clean music every X seconds", type=int, default=1800, show_default=True)
@click.option("--timeout", help="How many seconds until we terminate", type=int, show_default=True)
@syncify
@beartype
async def watch(
    musicdb: MusicDb,
    scan_folders: ScanFolders,
    sleep: int,
    timeout: int | None,
) -> None:
    async def soft_clean_periodically() -> None:
        try:
            while True:
                try:
                    cleaned = await musicdb.soft_clean()
                    MusicbotObject.success(cleaned)
                    MusicbotObject.success(f"DB cleaned, waiting {sleep} seconds.")
                    await asyncio.sleep(sleep)
                except edgedb.ClientConnectionFailedTemporarilyError as error:
                    MusicbotObject.err(f"{musicdb} : unable to clean musics", error=error)
        except (asyncio.CancelledError, KeyboardInterrupt):
            pass

    async def update_music(path: Path) -> None:
        for directory in scan_folders.directories:
            if str(path).startswith(str(directory)):
                if (file := File.from_path(folder=directory, path=path)) is None:
                    continue

                if (music_input := file.music_input) is None:
                    continue

                _ = await musicdb.upsert_music(music_input)

    async def watcher() -> None:
        class MusicWatchFilter(DefaultFilter):
            def __call__(self, change: Change, path: str) -> bool:
                return super().__call__(change, path) and path.endswith(tuple(scan_folders.extensions))

        try:
            async for changes in awatch(
                *scan_folders.directories,
                watch_filter=MusicWatchFilter(),
                debug=MusicbotObject.config.debug,
            ):
                try:
                    for change_path in changes:
                        change, path = change_path
                        if change in (Change.added, Change.modified):
                            await update_music(Path(path))
                        elif change == Change.deleted:
                            _ = await musicdb.remove_music_path(path)
                except edgedb.ClientConnectionFailedTemporarilyError as error:
                    MusicbotObject.err(f"{musicdb} : unable to clean musics", error=error)
        except (asyncio.CancelledError, KeyboardInterrupt):
            pass

    try:
        future = asyncio.gather(
            soft_clean_periodically(),
            watcher(),
        )
        _ = await asyncio.wait_for(future, timeout=timeout)
    except (TimeoutError, asyncio.CancelledError, KeyboardInterrupt):
        pass


@cli.command(short_help="Generate a new playlist", help=FILTERS_REPRS)
@musicdb_options
@output_option
@music_filters_options
@playlist_options
@click.argument("out", type=click.File("w", lazy=True), default="-")
@syncify
@beartype
async def playlist(
    output: str,
    music_filters: list[MusicFilter],
    playlist_options: PlaylistOptions,
    musicdb: MusicDb,
    out: click.utils.LazyFile,
) -> None:
    musicdb.set_readonly()
    await local.playlist(
        output=output,
        music_filters=music_filters,
        playlist_options=playlist_options,
        musicdb=musicdb,
        out=out,
    )


@cli.command(short_help="Artists descriptions")
@musicdb_options
@output_option
@syncify
@beartype
async def artists(
    output: str,
    musicdb: MusicDb,
) -> None:
    musicdb.set_readonly()
    all_artists = await musicdb.artists()
    table = Table(
        "Name",
        "Rating",
        "Size",
        "Length",
        "Albums",
        "Musics",
        "Keywords",
        "Genres",
        title="Artists",
    )
    for artist in all_artists:
        table.add_row(
            artist.name,
            str(artist.rating),
            artist.human_size,
            artist.human_duration,
            str(artist.n_albums),
            str(artist.n_musics),
            artist.all_keywords,
            artist.all_genres,
        )
    table.caption = f"{len(all_artists)} listed"

    if output == "table":
        MusicbotObject.print_table(table)
    elif output == "json":
        MusicbotObject.print_json([asdict(artist) for artist in all_artists])


@cli.command(short_help="Generate bests playlists with some rules", help=FILTERS_REPRS)
@scan_folder_argument
@music_filters_options
@musicdb_options
@dry_option
@playlist_options
@bests_options
@syncify
@beartype
async def bests(
    musicdb: MusicDb,
    music_filters: list[MusicFilter],
    scan_folder: Path,
    min_playlist_size: int,
    playlist_options: PlaylistOptions,
) -> None:
    musicdb.set_readonly()
    await local.bests(
        musicdb=musicdb,
        music_filters=music_filters,
        scan_folder=scan_folder,
        min_playlist_size=min_playlist_size,
        playlist_options=playlist_options,
    )


@cli.command(short_help="Copy selected musics with filters to destination folder", help=FILTERS_REPRS)
@destination_argument
@musicdb_options
@lazy_yes_option
@dry_option
@music_filters_options
@flat_option
@click.option("--delete", help="Delete files on destination if not present in library", is_flag=True)
@syncify
@beartype
async def sync(
    musicdb: MusicDb,
    music_filters: list[MusicFilter],
    delete: bool,
    destination: Path,
    yes: bool,
    flat: bool,
) -> None:
    musicdb.set_readonly()
    await local.sync(
        musicdb=musicdb,
        music_filters=music_filters,
        delete=delete,
        destination=destination,
        yes=yes,
        flat=flat,
    )


@cli.command(short_help="Generate custom playlists inside music folders (and for Buckethead)")
@musicdb_options
@scan_folder_argument
@playlist_options
@bests_options
@coroutines_option
@dry_option
@click.option("--fast/--no-fast", is_flag=True, default=False, show_default=True)
@syncify
@beartype
async def custom_playlists(
    musicdb: MusicDb,
    scan_folder: Path,
    min_playlist_size: int,
    playlist_options: PlaylistOptions,
    fast: bool,
) -> None:
    scan_folders = ScanFolders(directories=[scan_folder])
    if not fast:
        music_inputs = await local.scan(
            musicdb=musicdb,
            scan_folders=scan_folders,
        )
        _ = await musicdb.clean_musics()
        _ = await local.upsert_musics(
            musicdb=musicdb,
            music_inputs=music_inputs,
        )

    musicdb.set_readonly()

    MusicbotObject.success(f"{scan_folders} : flushing old m3u")
    scan_folders.flush_m3u()

    bests_music_filter = MusicFilter(
        min_rating=4.0,
        keyword="^((?!cutoff|bad|demo|intro).)",
    )
    await local.bests(
        musicdb=musicdb,
        music_filters=[bests_music_filter],
        scan_folder=scan_folder,
        min_playlist_size=min_playlist_size,
        playlist_options=playlist_options,
    )

    pike_keywords = await musicdb.query(
        "for keyword in (select Keyword {name} filter contains(array_agg(.musics.keywords.name), 'pike') and .musics.rating >= 4.0 and .musics.album.artist.name = 'Buckethead') union (keyword.name) except {'pike'}"
    )

    for pike_keyword in pike_keywords:
        MusicbotObject.success(f"Generating pike playlists for keyword {pike_keyword}")
        for rating in [4, 4.5, 5]:
            MusicbotObject.success(f"Generating playlist for {pike_keyword}_{rating}")
            pike_music_filter = MusicFilter(
                artist="Buckethead",
                min_rating=rating,
                keyword=rf"^(?=.*pike)(?=.*{pike_keyword}).*$",
            )
            out = click.utils.LazyFile(
                filename=f"{scan_folder}/Buckethead/Pikes/{pike_keyword}_{rating}.m3u",
                mode="w",
            )
            await local.playlist(
                musicdb=musicdb,
                output="m3u",
                music_filters=[pike_music_filter],
                playlist_options=playlist_options,
                out=out,
            )

    for rating in [4, 4.5, 5]:
        MusicbotObject.success(f"Generating playlist rating for Pikes {rating}")
        rating_music_filter = MusicFilter(
            artist="Buckethead",
            min_rating=rating,
            keyword="pike",
        )
        out = click.utils.LazyFile(
            filename=f"{scan_folder}/Buckethead/Pikes/rating_{rating}.m3u",
            mode="w",
        )
        await local.playlist(
            musicdb=musicdb,
            output="m3u",
            music_filters=[rating_music_filter],
            playlist_options=playlist_options,
            out=out,
        )
