import logging
import os

import acoustid  # type: ignore
import click
from beartype import beartype
from click_skeleton import AdvancedGroup
from click_skeleton.helpers import seconds_to_human

from musicbot.cli.file import acoustid_api_key_option, music_argument
from musicbot.file import File

logger = logging.getLogger(__name__)


@click.group('youtube', help='Youtube tool', cls=AdvancedGroup)
@beartype
def cli() -> None:
    pass


@cli.command(help='Search a youtube link with artist and title')
@click.argument('artist')
@click.argument('title')
@beartype
def search(artist: str, title: str) -> None:
    '''Search a youtube link with artist and title'''
    import youtube_dl  # type: ignore
    ydl_opts = {
        'format': 'bestaudio',
        'ignoreerrors': True,
        'skip_download': True,
        'quiet': True,
        'no_warnings': True,
    }
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            infos = ydl.extract_info(f"ytsearch1:'{artist} {title}'", download=False)
            for entry in infos['entries']:
                print(entry['webpage_url'])
    except Exception as e:  # pylint: disable=broad-except
        logger.error(e)


@cli.command(help='Download a youtube link with artist and title')
@click.argument('artist')
@click.argument('title')
@click.option('--path', default=None)
@beartype
def download(artist: str, title: str, path: str) -> None:
    import youtube_dl
    try:
        if not path:
            path = f"{artist} - {title}.mp3"
        ydl_opts = {
            'format': 'bestaudio/best',
            'cachedir': False,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': path,
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(f"ytsearch1:'{artist} {title}'", download=True)
    except youtube_dl.utils.DownloadError as e:
        logger.error(e)


@cli.command(help='Search a youtube link with artist and title')
@music_argument
@acoustid_api_key_option
@beartype
def find(file: File, acoustid_api_key: str) -> None:
    import youtube_dl
    yt_path = f"{file.artist} - {file.title}.mp3"
    try:
        file_id = file.fingerprint(acoustid_api_key)
        print(f'Searching for artist {file.artist} and title {file.title} and duration {seconds_to_human(file.length)}')
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'cachedir': False,
            'no_warnings': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': yt_path,
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            infos = ydl.extract_info(f"ytsearch1:'{file.artist} {file.title}'", download=True)
            url = None
            for entry in infos['entries']:
                url = entry['webpage_url']
                break

            yt_ids = acoustid.match(acoustid_api_key, yt_path)
            yt_id = None
            for _, recording_id, _, _ in yt_ids:
                yt_id = recording_id
                break
            if file_id == yt_id:
                print(f'Found: fingerprint {file_id} | url {url}')
            else:
                print(f'Not exactly found: fingerprint file: {file_id} | yt: {yt_id} | url {url}')
                print(f'Based only on duration, maybe: {url}')
    except acoustid.WebServiceError as e:
        logger.error(e)
    except youtube_dl.utils.DownloadError as e:
        logger.error(e)
    finally:
        try:
            if yt_path:
                os.remove(yt_path)
        except OSError:
            logger.warning(f"File not found: {yt_path}")


@cli.command(help='Fingerprint a youtube video')
@click.argument('url')
@acoustid_api_key_option
@beartype
def fingerprint(url: str, acoustid_api_key: str) -> None:
    import youtube_dl
    yt_path = "intermediate.mp3"
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': yt_path,
    }
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)
            yt_ids = acoustid.match(acoustid_api_key, yt_path)
            for _, recording_id, _, _ in yt_ids:
                print(recording_id)
                break
    except youtube_dl.utils.DownloadError as e:
        logger.error(e)
    except acoustid.WebServiceError as e:
        logger.error(e)
