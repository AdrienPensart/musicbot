import click
from logging import debug
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL, basicConfig

verbosities = {'debug': DEBUG,
               'info': INFO,
               'warning': WARNING,
               'error': ERROR,
               'critical': CRITICAL}

global_options = [
    click.option('--verbosity', help='Verbosity levels', default='error', type=click.Choice(verbosities.keys())),
    click.option('--dry-run', help='Take no real action', default=False, is_flag=True),
    click.option('--quiet', help='Silence any output (like progress bars)', default=False, is_flag=True)
]

db_options = [
    click.option('--host', help='DB host', default='localhost'),
    click.option('--port', help='DB port', default=5432),
    click.option('--db', help='DB name', default='musicbot'),
    click.option('--user', help='DB user', default='postgres'),
    click.option('--password', help='DB password', default='musicbot')
]

default_formats = ["mp3", "flac"]
filter_options = [
    click.option('--filter', help='Filter file to load'),
    click.option('--limit', help='Fetch a maximum limit of music'),
    click.option('--youtube', help='Select musics with a youtube link', default=None, is_flag=True),
    click.option('--formats', help='Select musics with file format, comma separated', default=','.join(default_formats)),
    click.option('--no-formats', help='Filter musics without format, comma separated, can be "None" for empty string'),
    click.option('--keywords', help='Select musics with keywords, comma separated, can be "None" for empty string'),
    click.option('--no-keywords', help='Filter musics without keywords, comma separated, can be "None" for empty string'),
    click.option('--artists', help='Select musics with artists, comma separated, can be "None" for empty string'),
    click.option('--no-artists', help='Filter musics without artists, comma separated, can be "None" for empty string'),
    click.option('--albums', help='Select musics with albums, comma separated, can be "None" for empty string'),
    click.option('--no-albums', help='Filter musics without albums, comma separated, can be "None" for empty string'),
    click.option('--titles', help='Select musics with titles, comma separated, can be "None" for empty string'),
    click.option('--no-titles', help='Filter musics without titless, comma separated, can be "None" for empty string'),
    click.option('--genres', help='Select musics with genres, comma separated, can be "None" for empty string'),
    click.option('--no-genres', help='Filter musics without genres, comma separated, can be "None" for empty string'),
    click.option('--min-duration', help='Minimum duration filter (hours:minutes:seconds)'),
    click.option('--max-duration', help='Maximum duration filter (hours:minutes:seconds))'),
    click.option('--min-size', help='Minimum file size filter (in bytes)'),
    click.option('--max-size', help='Maximum file size filter (in bytes)'),
    click.option('--min-rating', help='Minimum rating (between {default_min_rating} and {default_max_rating})'),
    click.option('--max-rating', help='Maximum rating (between {default_min_rating} and {default_max_rating})')
]


def add_options(options):
    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func
    return _add_options


class GlobalContext(object):
    def __init__(self):
        self.quiet = False
        self.dry_run = False
        self._verbosity = ERROR

    @property
    def verbosity(self):
        return self._verbosity

    @verbosity.setter
    def verbosity(self, verbosity):
        self._verbosity = verbosity
        basicConfig(level=verbosities[verbosity])
        debug('new verbosity: {}'.format(self.verbosity))


class DbContext(object):
    def __init__(self):
        self.host = 'localhost'
        self.port = 5432
        self.db = 'musicbot'
        self.user = 'postgres'
        self.password = 'musicbot'

    def connection_string(self):
        return 'postgresql://{}:{}@{}:{}/{}'.format(self.user, self.password, self.host, self.port, self.db)


global_context = click.make_pass_decorator(GlobalContext, ensure=True)
db_context = click.make_pass_decorator(DbContext, ensure=True)
