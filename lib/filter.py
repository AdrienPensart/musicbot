default_min_rating = 0.0
default_max_rating = 5.0
default_formats = ["mp3", "flac"]
min_int = 0
max_int = 2147483647
default_max_limit = max_int
default_min_size = min_int
default_max_size = max_int
default_min_duration = min_int
default_max_duration = max_int


class Filter(object):

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if value is not None:
                setattr(self, key, value)

    def to_list(self):
        # return [a for a in dir(self) if not a.startswith('__')]
        return [self.id,
                self.min_duration, self.max_duration,
                self.min_size, self.max_size,
                self.min_rating, self.max_rating,
                self.artists, self.no_artists,
                self.albums, self.no_albums,
                self.titles, self.no_titles,
                self.genres, self.no_genres,
                self.formats, self.no_formats,
                self.keywords, self.no_keywords,
                self.shuffle, self.limit, self.youtube]

    id = 0
    relative = False
    shuffle = False
    youtube = None
    formats = default_formats
    no_formats = list()
    genres = list()
    no_genres = list()
    limit = default_max_limit
    min_duration = default_min_duration
    max_duration = default_max_duration
    min_size = default_min_size
    max_size = default_max_size
    min_rating = default_min_rating
    max_rating = default_max_rating
    keywords = list()
    no_keywords = list()
    artists = list()
    no_artists = list()
    titles = list()
    no_titles = list()
    albums = list()
    no_albums = list()
    checks = list()
    no_checks = list()
