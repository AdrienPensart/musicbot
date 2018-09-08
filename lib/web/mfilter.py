import logging
import attr
from ..mfilter import Filter
from ..lib import num

logger = logging.getLogger(__name__)


# @attr.s(frozen=True)
class WebFilter(Filter):
    def __init__(self, request, **kwargs):
        for kw in request.args:
            if kw not in attr.fields_dict(Filter):
                continue
            default_value = attr.fields_dict(Filter)[kw].default
            if kw in ['name']:
                kwargs[kw] = request.args.get(kw, default_value)
            elif kw in ['youtubes', 'no_youtubes', 'formats', 'no_formats', 'artists', 'no_artists', 'genres', 'no_genres', 'albums', 'no_albums', 'titles', 'no_titles', 'keywords', 'no_keywords']:
                kwargs[kw] = request.args.getlist(kw, default_value)
            elif kw in ['min_rating', 'max_rating']:
                kwargs[kw] = float(request.args.get(kw, default_value))
            elif kw in ['shuffle', 'relative']:
                kwargs[kw] = bool(num(request.args.get(kw, default_value)))
            elif kw in ['limit', 'min_size', 'max_size', 'min_duration', 'min_duration']:
                kwargs[kw] = int(num(request.args.get(kw, default_value)))
            else:
                logger.warning('Keyword argument not known: %s', kw)
        super().__init__(**kwargs)
        logger.debug('WebFilter: %s', self)
