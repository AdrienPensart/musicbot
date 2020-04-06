import os
import logging
import click
import acoustid
from humanfriendly import format_timespan
from pytube import YouTube
from pytube.exceptions import VideoUnavailable
from tqdm import tqdm
from musicbot import helpers
from musicbot.config import config
from musicbot.music import youtube
from musicbot.music.file import File
from musicbot.music.youtube import youtube_api_key_option
from musicbot.music.fingerprint import acoustid_api_key_option

logger = logging.getLogger(__name__)


@click.group(cls=helpers.GroupWithHelp)
def cli():
    '''Youtube tool'''


@cli.command()
@helpers.add_options(youtube_api_key_option)
@click.argument('artist')
@click.argument('title')
def search(**kwargs):
    '''Search a youtube link with artist and title'''
    print(youtube.search(**kwargs))


@cli.command()
@click.argument('path')
@helpers.add_options(youtube_api_key_option + acoustid_api_key_option)
def find(path, acoustid_api_key, youtube_api_key):
    '''Search a youtube link with artist and title'''
    f = File(path)
    file_id = f.fingerprint(acoustid_api_key)

    print('Searching for artist {} and title {} and duration {}'.format(f.artist, f.title, format_timespan(f.duration)))
    urls = youtube.search(youtube_api_key, f.artist, f.title, f.duration)
    for url in urls:
        yt_path = None
        try:
            yt = YouTube(url)
            for stream in yt.streams.filter(only_audio=True):
                with tqdm(total=stream.filesize, desc="Testing {}".format(url), disable=config.quiet, leave=False) as pbar:
                    def show_progress_bar(stream, chunk, bytes_remaining):  # pylint: disable=unused-argument
                        pbar.update(len(chunk))  # pylint: disable=cell-var-from-loop
                    yt.register_on_progress_callback(show_progress_bar)
                    yt_path = stream.download()
                    break
            yt_ids = acoustid.match(acoustid_api_key, yt_path)
            yt_id = None
            for _, recording_id, _, _ in yt_ids:
                yt_id = recording_id
                break
            if file_id == yt_id:
                print('Found: fingerprint {} | url {}'.format(file_id, url))
                break
            if yt_id is not None:
                print('Not exactly found: fingerprint file: {} | yt: {} | url {}'.format(file_id, yt_id, url))
                break
            print('Based only on duration, maybe: {}'.format(url))
        except VideoUnavailable:
            pass
        finally:
            if yt_path:
                os.remove(yt_path)


@cli.command()
@click.argument('url')
@helpers.add_options(acoustid_api_key_option)
def fingerprint(url, acoustid_api_key):
    '''Fingerprint a youtube video'''
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(only_audio=True).order_by('abr').asc().first()
        with tqdm(total=stream.filesize, desc="Downloading music", disable=config.quiet, leave=False) as pbar:
            def show_progress_bar(stream, chunk, bytes_remaining):  # pylint: disable=unused-argument
                pbar.update(len(chunk))
            yt.register_on_progress_callback(show_progress_bar)
            path = stream.download()
        fps = acoustid.match(acoustid_api_key, path)
        for fp in fps:
            print(fp)
            break
    finally:
        os.remove(path)
