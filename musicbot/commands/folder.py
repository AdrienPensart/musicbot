import logging
from pathlib import Path

import click
import mutagen
from beartype import beartype
from click_skeleton import AdvancedGroup
from rich.table import Table

from musicbot.cli.file import file_options, flat_option, keywords_option
from musicbot.cli.options import output_option, threads_option
from musicbot.cli.scan_folders import destination_argument, scan_folders_argument
from musicbot import (
    File,
    MusicbotObject,
    Playlist,
    ScanFolders
)

logger = logging.getLogger(__name__)


@click.group("folder", help="Manage folders", cls=AdvancedGroup)
@beartype
def cli() -> None:
    pass


@cli.command(help="Just list music files")
@scan_folders_argument
@beartype
def find(scan_folders: ScanFolders) -> None:
    for file in scan_folders.files:
        print(file)


@cli.command(help="Generates a playlist", aliases=["tags", "musics", "tracks"])
@scan_folders_argument
@output_option
@beartype
def playlist(
    scan_folders: ScanFolders,
    output: str,
) -> None:
    name = str(scan_folders)
    playlist = Playlist(name=name, musics=scan_folders.musics)
    playlist.print(
        output=output,
    )


@cli.command(help="Convert all files in folders to mp3", aliases=["flac-to-mp3"])
@destination_argument
@scan_folders_argument
@threads_option
@flat_option
@output_option
@beartype
def flac2mp3(
    scan_folders: ScanFolders,
    destination: Path,
    output: str,
    threads: int,
    flat: bool,
) -> None:
    mp3_files = scan_folders.flac_to_mp3(
        destination=destination,
        threads=threads,
        flat=flat,
    )
    name = str(scan_folders)
    playlist = Playlist.from_files(
        name=name,
        files=mp3_files,
    )
    playlist.print(
        output=output,
    )


@cli.command(help="Show music files issues in folders")
@scan_folders_argument
@beartype
def issues(
    scan_folders: ScanFolders,
) -> None:
    table = Table("Path", "Issues")
    for file in scan_folders.files:
        try:
            if issues := file.issues:
                table.add_row(str(file.path), ", ".join(issues))
        except (OSError, mutagen.MutagenError):
            table.add_row(str(file.path), "could not open file")
    table.caption = f"{scan_folders} : {table.row_count} inconsistencies listed"
    MusicbotObject.print_table(table)


@cli.command(help="Fix music files in folders")
@scan_folders_argument
@beartype
def manual_fix(
    scan_folders: ScanFolders,
) -> None:
    def _manual_fix(file: File) -> None:
        MusicbotObject.warn(f"{file} : has issues : {file.issues}")
        if not file.fix():
            MusicbotObject.warn(f"{file} : unable to fixed !")

        if not (issues := file.issues):
            MusicbotObject.success(f"{file} : fixed !")
            return
        MusicbotObject.err(f"{file} : still issues : {issues}")

    for file in scan_folders.files:
        if file.music is None:
            continue
        print(file.music.human_repr())
        if not file.issues:
            continue
        _manual_fix(file)
        MusicbotObject.tip("Wait for Enter...")
        if MusicbotObject.is_tty:
            _ = input("")


@cli.command(help="Set music title", aliases=["set-tag"])
@scan_folders_argument
@file_options
@beartype
def set_tags(
    scan_folders: ScanFolders,
    title: str | None = None,
    artist: str | None = None,
    album: str | None = None,
    genre: str | None = None,
    keywords: list[str] | None = None,
    rating: float | None = None,
    track: int | None = None,
) -> None:
    for file in scan_folders.files:
        if not file.set_tags(
            title=title,
            artist=artist,
            album=album,
            genre=genre,
            keywords=keywords,
            rating=rating,
            track=track,
        ):
            MusicbotObject.err(f"{file} : unable to set tags")


@cli.command(help="Add keywords to music")
@keywords_option
@scan_folders_argument
@beartype
def add_keywords(
    scan_folders: ScanFolders,
    keywords: set[str],
) -> None:
    for file in scan_folders.files:
        if not file.add_keywords(keywords):
            MusicbotObject.err(f"{file} : unable to add keywords")


@cli.command(help="Delete keywords to music")
@keywords_option
@scan_folders_argument
@beartype
def delete_keywords(
    scan_folders: ScanFolders,
    keywords: set[str],
) -> None:
    for file in scan_folders.files:
        if not file.delete_keywords(keywords):
            MusicbotObject.err(f"{file} : unable to delete keywords")
