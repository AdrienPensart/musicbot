#!/usr/bin/env python

import logging
import isodate
import ujson
import aiohttp
from logging import debug

logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)
logging.getLogger('googleapiclient.discovery').setLevel(logging.CRITICAL)

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


async def search(artist, title, duration):
    try:
        string = ' '.join([artist, title])
        parsingChannelUrl = "https://www.googleapis.com/youtube/v3/search"
        parsingChannelHeader = {'cache-control': "no-cache"}
        parsingChannelQueryString = {"part": "id,snippet", "maxResults": "10",
                                     "key": DEVELOPER_KEY, "type": "video", "q": string, "safeSearch": "none", "videoDuration": youtube_duration(duration)}
        parsingChannel = None
        async with aiohttp.ClientSession() as session:
            async with session.get(parsingChannelUrl, headers=parsingChannelHeader, params=parsingChannelQueryString) as resp:
                parsingChannel = await resp.read()
        parsingChannelItems = ujson.loads(parsingChannel).get("items")
        if parsingChannelItems is None or not len(parsingChannelItems):
            return 'not found'
        VideoIds = ",".join(str(x.get("id").get("videoId")) for x in parsingChannelItems)

        parsingVideoUrl = "https://www.googleapis.com/youtube/v3/videos"
        parsingVideoHeader = {'cache-control': "no-cache"}
        parsingVideoQueryString = {"part": 'id,snippet,contentDetails', "id": VideoIds, "key": DEVELOPER_KEY}
        parsingVideo = None
        async with aiohttp.ClientSession() as session:
            async with session.get(parsingVideoUrl, headers=parsingVideoHeader, params=parsingVideoQueryString) as resp:
                parsingVideo = await resp.read()
        results = ujson.loads(parsingVideo).get("items")
        if results is None:
            return 'not found'

        mapping = {r["id"]: isodate.parse_duration(r["contentDetails"]["duration"]).total_seconds() for r in results}
        debug("duration: {}, mapping: {}".format(duration, mapping))
        key = min(mapping, key=lambda k: abs(mapping[k] - duration))
        url = "https://www.youtube.com/watch?v={}".format(key)
        debug("Most relevant: {} {} {}".format(key, mapping[key], url))
        return url
    except:
        debug('Cannot find video for artist: {} title: {} duration: {}'.format(artist, title, duration))
        # import traceback
        # import pprint
        # pprint(traceback.format_exc())
        return 'error'


# from apiclient.discovery import build
# from apiclient.errors import HttpError
# def list_playlists(**kwargs):
#     youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY, cache_discovery=False)
#     results = youtube.playlists().list(**kwargs).execute()
#     print(results)
#
#
# def new_playlist(**kwargs):
#     youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY, cache_discovery=False)
#     results = youtube.playlists().insert(body={'snippet.title': '', 'snippet.description': '', 'snippet.tags[]': '', 'snippet.defaultLanguage': '', 'status.privacyStatus': ''}, part='snippet,status', onBehalfOfContentOwner='').execute()
#     print(results)
#
#
# def search(artist, title, duration):
#     try:
#         youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
#
#         string = ' '.join([artist, title])
#         search_response = youtube.search().list(
#             q=string,
#             type="video",
#             part="id,snippet",
#             maxResults=10,
#             safeSearch="none",
#             videoDuration=youtube_duration(duration)
#         ).execute()
#
#         videoIds = ','.join([result["id"].get("videoId", '') for result in search_response.get("items", [])])
#         debug("IDs: {}".format(videoIds))
#
#         results = youtube.videos().list(
#             id=videoIds,
#             part='id,snippet,contentDetails'
#         ).execute()
#
#         if not len(results.get("items", [])):
#             return 'not found'
#
#         mapping = {r["id"]: isodate.parse_duration(r["contentDetails"]["duration"]).total_seconds() for r in results.get("items", [])}
#         debug("duration: {}, mapping: {}".format(duration, mapping))
#         key = min(mapping, key=lambda k: abs(mapping[k] - duration))
#         url = "https://www.youtube.com/watch?v={}".format(key)
#         debug("Most relevant: {} {} {}".format(key, mapping[key], url))
#         return url
#
#     except HttpError as e:
#         error("An HTTP error {} occurred: {}".format(e.resp.status, e.content))
#         return 'error'
