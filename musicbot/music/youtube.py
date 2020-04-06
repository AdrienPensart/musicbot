import logging
import isodate
import click
import requests
from humanfriendly import format_timespan
from musicbot.helpers import config_string

logger = logging.getLogger(__name__)
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)
logging.getLogger('googleapiclient.discovery').setLevel(logging.CRITICAL)

YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

DEFAULT_YOUTUBE_API_KEY = None
youtube_api_key_option = [click.option('--youtube-api-key', help='YouTube API Key', default=DEFAULT_YOUTUBE_API_KEY, callback=config_string)]


def youtube_duration(dur):
    if dur is None:
        return "any"
    if 0 <= dur <= 4 * 60:
        return "short"
    if 4 * 60 < dur <= 20 * 60:
        return "medium"
    if dur > 20 * 60:
        return "long"
    return "any"


# pylint: disable-msg=too-many-locals
def search(youtube_api_key, artist, title, duration=None):
    try:
        string = ' '.join([artist, title])
        parsingChannelUrl = "https://www.googleapis.com/youtube/v3/search"
        parsingChannelHeader = {'cache-control': "no-cache"}
        parsingChannelQueryString = {"part": "id,snippet", "maxResults": "10",
                                     "key": youtube_api_key, "type": "video", "q": string, "safeSearch": "none", "videoDuration": youtube_duration(duration)}
        parsingChannel = None

        resp = requests.get(parsingChannelUrl, headers=parsingChannelHeader, params=parsingChannelQueryString)
        parsingChannel = resp.json()

        parsingChannelItems = parsingChannel.get("items")
        if parsingChannelItems is None or not parsingChannelItems:
            return []
        VideoIds = ",".join(str(x.get("id").get("videoId")) for x in parsingChannelItems)

        parsingVideoUrl = "https://www.googleapis.com/youtube/v3/videos"
        parsingVideoHeader = {'cache-control': "no-cache"}
        parsingVideoQueryString = {"part": 'id,snippet,contentDetails', "id": VideoIds, "key": youtube_api_key}
        parsingVideo = None

        resp = requests.get(parsingVideoUrl, headers=parsingVideoHeader, params=parsingVideoQueryString)
        parsingVideo = resp.json()
        results = parsingVideo.get("items")
        if results is None:
            return []

        for r in results:
            logger.info('%s %s', r["snippet"]["title"], format_timespan(isodate.parse_duration(r["contentDetails"]["duration"]).total_seconds()))
        if duration:
            mapping = {"https://www.youtube.com/watch?v=" + r["id"]: abs(isodate.parse_duration(r["contentDetails"]["duration"]).total_seconds() - duration) for r in results}
            links = sorted(mapping, key=mapping.get)
            return links
        return ["https://www.youtube.com/watch?v=" + r["id"] for r in results]
    except Exception as e:  # pylint: disable=broad-except
        logger.info(type(e))
        logger.info('Cannot find video for artist: %s title: %s duration: %s', artist, title, duration)
        return []
