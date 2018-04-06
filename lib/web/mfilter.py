# -*- coding: utf-8 -*-
from logging import debug
from ..mfilter import Filter
from ..lib import num


class WebFilter(Filter):
    def __init__(self, request, **kwargs):
        super().__init__(**kwargs)
        self.youtube = request.args.get('youtube', self.youtube)
        self.name = request.args.get('name', self.youtube)
        for param in ['formats', 'no_formats', 'artists', 'no_artists', 'genres', 'no_genres', 'albums', 'no_albums', 'titles', 'no_titles', 'keywords', 'no_keywords']:
            data = request.args.getlist(param, getattr(self, param))
            setattr(self, param, data)

        for param in ['min_rating', 'max_rating']:
            data = request.args.get(param, getattr(self, param))
            setattr(self, param, float(data))

        for param in ['shuffle', 'relative']:
            data = num(request.args.get(param, getattr(self, param)))
            setattr(self, param, bool(data))

        for param in ['limit', 'min_size', 'max_size', 'min_duration', 'min_duration']:
            data = num(request.args.get(param, getattr(self, param)))
            setattr(self, param, int(data))
        debug('WebFilter: {}'.format(self))
