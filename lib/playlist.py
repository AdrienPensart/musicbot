import os
import codecs
import random
from logging import warning, info

default_playlist_type = 'm3u'
playlist_types = ['list', 'm3u']


class Playlist(object):

    type = default_playlist_type
    path = '.'

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if value is not None:
                setattr(self, key, value)

    def generate(self, musics, mf):
        lines = []
        for m in musics:
            if mf.relative:
                beginning = os.path.join(m.folder + '/')
                if m.path.startswith(beginning):
                    lines.append(m.path[len(beginning):])
                else:
                    warning("Invalid beginning for relative path {} beginning is {}".format(m.path, beginning))
                    continue
            else:
                lines.append(m['path'])
        if mf.shuffle:
            random.shuffle(lines)
        else:
            lines.sort()
        if self.type == 'm3u':
            lines.insert(0, "#EXTM3U")
        elif self.type != 'list':
            raise ValueError(self.type)
        content = "\n".join(lines)

        if self.path != '.':
            with codecs.open(self.path, 'w', "utf-8-sig") as m3u:
                m3u.write(content)
        else:
            info('Output to stdout')
            print(content)
