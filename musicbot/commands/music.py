import logging
from dataclasses import asdict
from pathlib import Path

import click
from beartype import beartype
from click_skeleton import AdvancedGroup
from mutagen import MutagenError
from rich.table import Table

from musicbot import MusicbotObject
from musicbot.cli.file import (
    acoustid_api_key_option,
    file_argument,
    file_options,
    keywords_arguments,
    paths_arguments,
)
from musicbot.cli.folder import destination_argument
from musicbot.cli.options import dry_option, output_option
from musicbot.file import File

logger = logging.getLogger(__name__)


@click.group("music", help="Music file", cls=AdvancedGroup, aliases=["file"])
@beartype
def cli() -> None:
    pass


@cli.command(help="Show music")
@file_argument
@beartype
def show(
    file: File,
) -> None:
    MusicbotObject.success(f"{file.folder=}")
    MusicbotObject.success(f"{file.path=}")
    MusicbotObject.success(f"{file.filename=}")
    MusicbotObject.success(f"{file.extension=}")
    MusicbotObject.success(f"{file.title=}")
    MusicbotObject.success(f"{file.artist=}")
    MusicbotObject.success(f"{file.album=}")
    MusicbotObject.success(f"{file.genre=}")
    MusicbotObject.success(f"{file.rating=}")
    MusicbotObject.success(f"{file.track=}")
    MusicbotObject.success(f"{file.keywords=}")
    MusicbotObject.success(f"{file.issues=}")
    MusicbotObject.success(f"{file.size=}")
    MusicbotObject.success(f"{file.length=} ")
    MusicbotObject.success(f"{file.canonic_artist_album_filename=}")
    MusicbotObject.success(f"{file.canonic_title=}")
    MusicbotObject.success(f"{file.canonic_filename=}")
    MusicbotObject.success(f"{file.canonic_path=}")
    MusicbotObject.success(f"{file.flat_title=}")
    MusicbotObject.success(f"{file.flat_filename=}")
    MusicbotObject.success(f"{file.flat_path=}")


@cli.command(help="Convert flac music to mp3", aliases=["flac-to-mp3"])
@file_argument
@destination_argument
@dry_option
@beartype
def flac2mp3(file: File, destination: Path) -> None:
    if not file.to_mp3(destination):
        MusicbotObject.err(f"{file} : unable to convert to MP3")


@cli.command(help="Print music fingerprint")
@file_argument
@acoustid_api_key_option
@beartype
def fingerprint(file: File, acoustid_api_key: str) -> None:
    if (file_fingerprint := file.fingerprint(acoustid_api_key)) is None:
        return
    print(file_fingerprint)


@cli.command(help="Print music tags", aliases=["tag"])
@file_argument
@output_option
@beartype
def tags(
    file: File,
    output: str,
) -> None:
    logger.info(file.handle.tags.keys())
    if (music := file.music) is None:
        raise click.ClickException("unable to continue")

    if output == "json":
        MusicbotObject.print_json(asdict(music))
        return
    print(music.human_repr())


@cli.command(help="Check music consistency")
@file_argument
@beartype
def issues(
    file: File,
) -> None:
    table = Table("Path", "Issues")
    try:
        if issues := file.issues:
            table.add_row(str(file.path), ", ".join(issues))
    except (OSError, MutagenError):
        table.add_row(str(file.path), "could not open file")
    MusicbotObject.console.print(table)


@cli.command(help="Fix music file")
@file_argument
@dry_option
@beartype
def manual_fix(
    file: File,
) -> None:
    if (music := file.music) is None:
        raise click.ClickException("unable to continue")

    print(music.human_repr())
    if not (issues := file.issues):
        return
    MusicbotObject.warn(f"{file} : has issues : {issues}")

    if not file.fix():
        MusicbotObject.warn(f"{file} : unable to fix !")

    if issues:
        MusicbotObject.err(f"{file} : still issues : {issues}")
    else:
        MusicbotObject.success(f"{file} : fixed !")


@cli.command(help="Set music title", aliases=["set-tag"])
@paths_arguments
@dry_option
@file_options
@beartype
def set_tags(
    paths: list[Path],
    title: str | None = None,
    artist: str | None = None,
    album: str | None = None,
    genre: str | None = None,
    keywords: list[str] | None = None,
    rating: float | None = None,
    track: int | None = None,
) -> None:
    for path in paths:
        file = File.from_path(folder=path.parent, path=path)
        if not file:
            continue
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
@file_argument
@keywords_arguments
@dry_option
@beartype
def add_keywords(file: File, keywords: set[str]) -> None:
    if not file.add_keywords(keywords):
        MusicbotObject.err(f"{file} : unable to add keywords")


@cli.command(help="Delete keywords to music", aliases=["delete-keyword", "remove-keywords", "remove-keyword"])
@file_argument
@keywords_arguments
@dry_option
@beartype
def delete_keywords(file: File, keywords: set[str]) -> None:
    if not file.delete_keywords(keywords):
        MusicbotObject.err(f"{file} : unable to delete keywords")


@cli.command(help="Replace one keyword in music")
@file_argument
@dry_option
@beartype
@click.argument("old_keyword")
@click.argument("new_keyword")
def replace_keyword(file: File, old_keyword: str, new_keyword: str) -> None:
    if not file.delete_keywords({old_keyword}):
        MusicbotObject.err(f"{file} : unable to delete keyword {old_keyword}")
    if not file.add_keywords({new_keyword}):
        MusicbotObject.err(f"{file} : unable to add keyword {new_keyword}")
