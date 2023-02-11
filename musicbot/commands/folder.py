import logging
from pathlib import Path

import click
import mutagen
from beartype import beartype
from click_skeleton import AdvancedGroup
from rich.table import Table

from musicbot.cli.file import file_options, flat_option, keywords_arguments
from musicbot.cli.folder import destination_argument, folders_argument
from musicbot.cli.options import dry_option, output_option, threads_option
from musicbot.file import File
from musicbot.folders import Folders
from musicbot.object import MusicbotObject
from musicbot.playlist import Playlist

logger = logging.getLogger(__name__)


@click.group("folder", help="Manage folders", cls=AdvancedGroup)
@beartype
def cli() -> None:
    pass


@cli.command(help="Just list music files")
@folders_argument
@beartype
def find(folders: Folders) -> None:
    for file in folders.files:
        print(file)


@cli.command(help="Generates a playlist", aliases=["tags", "musics", "tracks"])
@folders_argument
@output_option
@beartype
def playlist(
    folders: Folders,
    output: str,
) -> None:
    name = str(folders)
    playlist = Playlist(name=name, musics=folders.musics)
    playlist.print(
        output=output,
    )


@cli.command(help="Convert all files in folders to mp3", aliases=["flac-to-mp3"])
@destination_argument
@folders_argument
@threads_option
@flat_option
@output_option
@beartype
def flac2mp3(
    folders: Folders,
    destination: Path,
    output: str,
    threads: int,
    flat: bool,
) -> None:
    mp3_files = folders.flac_to_mp3(
        destination=destination,
        threads=threads,
        flat=flat,
    )
    name = str(folders)
    playlist = Playlist.from_files(
        name=name,
        files=mp3_files,
    )
    playlist.print(
        output=output,
    )


@cli.command(help="Show music files issues in folders")
@folders_argument
@beartype
def issues(
    folders: Folders,
) -> None:
    table = Table("Path", "Issues")
    for file in folders.files:
        try:
            if issues := file.issues:
                table.add_row(str(file.path), ", ".join(issues))
        except (OSError, mutagen.MutagenError):
            table.add_row(str(file.path), "could not open file")
    table.caption = f"{folders} : {table.row_count} inconsistencies listed"
    MusicbotObject.print_table(table)


@cli.command(help="Fix music files in folders")
@folders_argument
@beartype
def manual_fix(
    folders: Folders,
) -> None:
    def _manual_fix(file: File) -> None:
        MusicbotObject.warn(f"{file} : has issues : {file.issues}")
        if not file.fix():
            MusicbotObject.warn(f"{file} : unable to fixed !")

        if not (issues := file.issues):
            MusicbotObject.success(f"{file} : fixed !")
            return
        MusicbotObject.err(f"{file} : still issues : {issues}")

    for file in folders.files:
        if file.music is None:
            continue
        print(file.music.human_repr())
        if not file.issues:
            continue
        _manual_fix(file)
        MusicbotObject.tip("Wait for Enter...")
        _ = input("")


@cli.command(help="Set music title", aliases=["set-tag"])
@folders_argument
@dry_option
@file_options
@beartype
def set_tags(
    folders: Folders,
    title: str | None = None,
    artist: str | None = None,
    album: str | None = None,
    genre: str | None = None,
    keywords: list[str] | None = None,
    rating: float | None = None,
    track: int | None = None,
) -> None:
    for file in folders.files:
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
@folders_argument
@keywords_arguments
@dry_option
@beartype
def add_keywords(
    folders: Folders,
    keywords: set[str],
) -> None:
    for file in folders.files:
        if not file.add_keywords(keywords):
            MusicbotObject.err(f"{file} : unable to add keywords")


@cli.command(help="Delete keywords to music")
@folders_argument
@keywords_arguments
@dry_option
@beartype
def delete_keywords(
    folders: Folders,
    keywords: set[str],
) -> None:
    for file in folders.files:
        if not file.delete_keywords(keywords):
            MusicbotObject.err(f"{file} : unable to delete keywords")
