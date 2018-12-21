import logging
import isodate
import requests

logger = logging.getLogger(__name__)
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)
logging.getLogger('googleapiclient.discovery').setLevel(logging.CRITICAL)

DEVELOPER_KEY = "AIzaSyAm3XZ3OYj-GlNIHk-YFvpzrtvQ3ZalAoI"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


def youtube_duration(dur):
    if 0 <= dur <= 4 * 60:
        return "short"
    if 4 * 60 < dur <= 20 * 60:
        return "medium"
    if dur > 20 * 60:
        return "long"
    return "any"


# pylint: disable-msg=too-many-locals
def search(artist, title, duration):
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
            return 'not found'
        VideoIds = ",".join(str(x.get("id").get("videoId")) for x in parsingChannelItems)

        parsingVideoUrl = "https://www.googleapis.com/youtube/v3/videos"
        parsingVideoHeader = {'cache-control': "no-cache"}
        parsingVideoQueryString = {"part": 'id,snippet,contentDetails', "id": VideoIds, "key": DEVELOPER_KEY}
        parsingVideo = None

        resp = requests.get(parsingVideoUrl, headers=parsingVideoHeader, params=parsingVideoQueryString)
        parsingVideo = resp.json()
        results = parsingVideo.get("items")
        if results is None:
            return 'not found'

        mapping = {r["id"]: isodate.parse_duration(r["contentDetails"]["duration"]).total_seconds() for r in results}
        logger.debug("duration: %s, mapping: %s", duration, mapping)
        key = min(mapping, key=lambda k: abs(mapping[k] - duration))
        url = "https://www.youtube.com/watch?v={}".format(key)
        logger.debug("Most relevant: %s %s %s", key, mapping[key], url)
        return url
    except Exception as e:
        logger.debug(e)
        logger.debug('Cannot find video for artist: %s title: %s duration: %s', artist, title, duration)
        return 'error'
