import logging
import isodate
import requests
from humanfriendly import format_timespan

logger = logging.getLogger(__name__)
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)
logging.getLogger('googleapiclient.discovery').setLevel(logging.CRITICAL)

DEVELOPER_KEY = "AIzaSyAm3XZ3OYj-GlNIHk-YFvpzrtvQ3ZalAoI"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


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
def search(artist, title, duration=None):
    try:
        string = ' '.join([artist, title])
        parsingChannelUrl = "https://www.googleapis.com/youtube/v3/search"
        parsingChannelHeader = {'cache-control': "no-cache"}
        parsingChannelQueryString = {"part": "id,snippet", "maxResults": "10",
                                     "key": DEVELOPER_KEY, "type": "video", "q": string, "safeSearch": "none", "videoDuration": youtube_duration(duration)}
        parsingChannel = None

        resp = requests.get(parsingChannelUrl, headers=parsingChannelHeader, params=parsingChannelQueryString)
        parsingChannel = resp.json()

        parsingChannelItems = parsingChannel.get("items")
        if parsingChannelItems is None or not parsingChannelItems:
            return []
        VideoIds = ",".join(str(x.get("id").get("videoId")) for x in parsingChannelItems)

        parsingVideoUrl = "https://www.googleapis.com/youtube/v3/videos"
        parsingVideoHeader = {'cache-control': "no-cache"}
        parsingVideoQueryString = {"part": 'id,snippet,contentDetails', "id": VideoIds, "key": DEVELOPER_KEY}
        parsingVideo = None

        resp = requests.get(parsingVideoUrl, headers=parsingVideoHeader, params=parsingVideoQueryString)
        parsingVideo = resp.json()
        results = parsingVideo.get("items")
        if results is None:
            return []

        for r in results:
            logger.info('{} {}'.format(r["snippet"]["title"], format_timespan(isodate.parse_duration(r["contentDetails"]["duration"]).total_seconds())))
        if duration:
            mapping = {"https://www.youtube.com/watch?v=" + r["id"]: abs(isodate.parse_duration(r["contentDetails"]["duration"]).total_seconds() - duration) for r in results}
            links = sorted(mapping, key=mapping.get)
            return links
        return ["https://www.youtube.com/watch?v=" + r["id"] for r in results]
    except Exception as e:
        logger.info(type(e))
        logger.info('Cannot find video for artist: %s title: %s duration: %s', artist, title, duration)
        return []
