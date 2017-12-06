# -*- coding: utf-8 -*-
from logging import debug
from ..filter import Filter
from ..lib import num
from ..file import mysplit


class WebFilter(Filter):
    def __init__(self, request, **kwargs):
        super().__init__(**kwargs)
        youtube = request.args.get('youtube', self.youtube)
        if youtube == "2":
            self.youtube = None
        elif youtube == "1":
            self.youtube = True
        elif youtube == "0":
            self.youtube = False
        else:
            debug("bad value for youtube: {} {}".format(type(youtube), youtube))
        debug('youtube: {} {}'.format(youtube, self.youtube))

        self.shuffle = request.args.get('shuffle', getattr(self, 'shuffle'))
        debug('shuffle : {}'.format(self.shuffle))
        self.relative = request.args.get('relative', getattr(self, 'relative'))
        debug('relative: {}'.format(self.relative))

        for param in ['formats', 'no_formats', 'artists', 'no_artists', 'genres', 'no_genres', 'albums', 'no_albums', 'titles', 'no_titles', 'keywords', 'no_keywords']:
            raw = request.args.get(param, getattr(self, param))
            data = mysplit(raw, '","')
            if len(data) == 1 and data[0].startswith('"') and data[0].endswith('"'):
                data[0] = data[0][1:-1]
            debug('{} {}'.format(param, data))
            setattr(self, param, data)

        for param in ['min_rating', 'max_rating']:
            data = request.args.get(param, getattr(self, param))
            debug('{} {}'.format(param, data))
            setattr(self, param, data)

        for param in ['limit', 'min_size', 'max_size', 'min_duration', 'min_duration']:
            data = num(request.args.get(param, getattr(self, param)))
            debug('{} {}'.format(param, data))
            setattr(self, param, data)
