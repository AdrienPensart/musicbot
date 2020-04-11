import os
import logging
import click
import acoustid
import youtube_dl
from humanfriendly import format_timespan
from musicbot import helpers
# from musicbot.config import config
from musicbot.music.file import File
from musicbot.music.fingerprint import acoustid_api_key_option

logger = logging.getLogger(__name__)


@click.group(help='Youtube tool', cls=helpers.GroupWithHelp)
def cli():
    pass


@cli.command(help='Search a youtube link with artist and title')
@click.argument('artist')
@click.argument('title')
def search(artist, title):
    '''Search a youtube link with artist and title'''
    ydl_opts = {
        'format': 'bestaudio',
        'skip_download': True,
        'quiet': True,
        'no_warnings': True,
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        infos = ydl.extract_info(f"ytsearch1:'{artist} {title}'", download=False)
        for entry in infos['entries']:
            print(entry['webpage_url'])


@cli.command(help='Download a youtube link with artist and title')
@click.argument('artist')
@click.argument('title')
@click.option('--path', default=None)
def download(artist, title, path):
    if not path:
        path = f"{artist} - {title}.mp3"
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': path,
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(f"ytsearch1:'{artist} {title}'", download=True)


@cli.command(help='Search a youtube link with artist and title')
@click.argument('path')
@helpers.add_options(acoustid_api_key_option)
def find(path, acoustid_api_key):
    f = File(path)
    yt_path = f"{f.artist} - {f.title}.mp3"
    try:
        file_id = f.fingerprint(acoustid_api_key)
        print(f'Searching for artist {f.artist} and title {f.title} and duration {format_timespan(f.duration)}')
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
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            infos = ydl.extract_info(f"ytsearch1:'{f.artist} {f.title}'", download=True)
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
    finally:
        try:
            if yt_path:
                os.remove(yt_path)
        except FileNotFoundError:
            logger.warning(f"File not found: {yt_path}")


@cli.command(help='Fingerprint a youtube video')
@click.argument('url')
@helpers.add_options(acoustid_api_key_option)
def fingerprint(url, acoustid_api_key):
    yt_path = f"intermediate.mp3"
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
    except acoustid.WebServiceError as e:
        logger.error(e)
