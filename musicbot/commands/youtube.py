import logging
from pathlib import Path

import acoustid  # type: ignore
import click
from beartype import beartype
from beartype.typing import Any
from click_skeleton import AdvancedGroup
from click_skeleton.helpers import seconds_to_human

from musicbot import File, MusicbotObject
from musicbot.cli.file import acoustid_api_key_option, file_argument

logger = logging.getLogger(__name__)


class YoutubeLogger:
    def debug(self, msg: str) -> None:
        if msg.startswith("[debug] "):
            logging.debug(msg)
        else:
            logging.info(msg)

    def info(self, msg: str) -> None:
        logging.info(msg)

    def warning(self, msg: str) -> None:
        logging.warning(msg)

    def error(self, msg: str) -> None:
        logging.error(msg)


def youtube_hook(d: Any) -> None:
    if d["status"] == "finished":
        MusicbotObject.success("Done downloading, now post-processing ...")


@click.group("youtube", help="Youtube tool", cls=AdvancedGroup)
@beartype
def cli() -> None:
    pass


@cli.command(help="Search a youtube link with artist and title")
@click.argument("artist")
@click.argument("title")
@beartype
def search(artist: str, title: str) -> None:
    """Search a youtube link with artist and title"""
    import yt_dlp  # type: ignore

    ydl_opts = {
        "format": "ba",
        "ignoreerrors": True,
        "skip_download": True,
        "quiet": True,
        "no_warnings": True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            infos: dict = ydl.extract_info(f"ytsearch1:'{artist} {title}'", download=False)
            print(type(infos))
            for entry in infos["entries"]:
                print(entry["webpage_url"])
    except Exception as error:
        MusicbotObject.err(f"Unable to search for {artist=} and {title=}", error=error)


@cli.command(help="Download a youtube link with artist and title")
@click.argument("artist")
@click.argument("title")
@click.option("--path", default=None)
@beartype
def download(artist: str, title: str, path: str | None) -> None:
    import yt_dlp

    try:
        if path:
            final_filepath = Path(path).stem
        else:
            final_filepath = f"{artist} - {title}"
        ydl_opts = {
            "format": "ba",
            "cachedir": False,
            "logger": YoutubeLogger(),
            "progress_hooks": [youtube_hook],
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
            "outtmpl": final_filepath + ".%(ext)s",
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            _ = ydl.extract_info(f"ytsearch1:'{artist} {title}'", download=True)
    except yt_dlp.utils.DownloadError as e:
        logger.error(e)


@cli.command(help="Search a youtube link with artist and title")
@file_argument
@acoustid_api_key_option
@beartype
def find(file: File, acoustid_api_key: str) -> None:
    import yt_dlp

    filename = f"{file.artist} - {file.title}"
    final_path = Path(f"{filename}.mp3")
    try:
        final_path.unlink()
    except FileNotFoundError:
        pass

    ydl_opts = {
        "format": "ba",
        "quiet": True,
        "cachedir": False,
        "no_warnings": True,
        "logger": YoutubeLogger(),
        "progress_hooks": [youtube_hook],
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "outtmpl": filename + ".%(ext)s",
    }
    try:
        file_id = file.fingerprint(acoustid_api_key)
        print(f"Searching for artist {file.artist} and title {file.title} and duration {seconds_to_human(file.length)}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            infos: dict = ydl.extract_info(f"ytsearch1:'{file.artist} {file.title}'", download=True)
            url = None
            for entry in infos["entries"]:
                url = entry["webpage_url"]
                break

            yt_ids = acoustid.match(acoustid_api_key, str(final_path))
            yt_id = None
            for _, recording_id, _, _ in yt_ids:
                yt_id = recording_id
                break
            if file_id == yt_id:
                print(f"Found: fingerprint {file_id} | url {url}")
            else:
                print(f"Not exactly found: fingerprint file: {file_id} | yt: {yt_id} | url {url}")
                print(f"Based only on duration, maybe: {url}")
    except acoustid.WebServiceError as e:
        logger.error(e)
    except yt_dlp.utils.DownloadError as e:
        logger.error(e)
    finally:
        try:
            final_path.unlink()
        except FileNotFoundError:
            pass


@cli.command(help="Fingerprint a youtube video")
@click.argument("url")
@acoustid_api_key_option
@beartype
def fingerprint(url: str, acoustid_api_key: str) -> None:
    import yt_dlp

    name = "intermediate"
    final_path = Path(f"{name}.mp3")
    try:
        final_path.unlink()
    except FileNotFoundError:
        pass

    ydl_opts = {
        "format": "ba",
        "logger": YoutubeLogger(),
        "progress_hooks": [youtube_hook],
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "outtmpl": f"{name}.%(ext)s",
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            _ = ydl.download([url])
            yt_ids = acoustid.match(acoustid_api_key, str(final_path))
            for _, recording_id, _, _ in yt_ids:
                print(recording_id)
                break
    except yt_dlp.utils.DownloadError as e:
        logger.error(e)
    except acoustid.WebServiceError as e:
        logger.error(e)
    finally:
        try:
            final_path.unlink()
        except FileNotFoundError:
            pass
