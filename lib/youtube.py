#!/usr/bin/env python

from apiclient.discovery import build
from apiclient.errors import HttpError
from logging import debug, error
import isodate


DEVELOPER_KEY = "AIzaSyAm3XZ3OYj-GlNIHk-YFvpzrtvQ3ZalAoI"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


def youtube_duration(dur):
    if dur >= 0 and dur <= 4 * 60:
        return "short"
    if dur > 4 * 60 and dur <= 20 * 60:
        return "medium"
    if dur > 20 * 60:
        return "long"
    return "any"


def list_playlists(**kwargs):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY, cache_discovery=False)
    results = youtube.playlists().list(**kwargs).execute()
    print(results)


def new_playlist(**kwargs):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY, cache_discovery=False)
    results = youtube.playlists().insert(body={'snippet.title': '', 'snippet.description': '', 'snippet.tags[]': '', 'snippet.defaultLanguage': '', 'status.privacyStatus': ''}, part='snippet,status', onBehalfOfContentOwner='').execute()
    print(results)


def search(artist, title, duration):
    try:
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

        string = ' '.join([artist, title])
        search_response = youtube.search().list(
            q=string,
            type="video",
            part="id,snippet",
            maxResults=10,
            safeSearch="none",
            videoDuration=youtube_duration(duration)
        ).execute()

        videoIds = ','.join([result["id"].get("videoId",'') for result in search_response.get("items", [])])
        debug("IDs: {}".format(videoIds))

        results = youtube.videos().list(
            id=videoIds,
            part='id,snippet,contentDetails'
        ).execute()

        if not len(results.get("items", [])):
            return None

        mapping = {r["id"]: isodate.parse_duration(r["contentDetails"]["duration"]).total_seconds() for r in results.get("items", [])}
        debug("duration: {}, mapping: {}".format(duration, mapping))
        key = min(mapping, key=lambda k: abs(mapping[k] - duration))
        url = "https://www.youtube.com/watch?v={}".format(key)
        debug("Most relevant: {} {} {}".format(key, mapping[key], url))
        return url

    except HttpError as e:
        error("An HTTP error {} occurred: {}".format(e.resp.status, e.content))
        return None
