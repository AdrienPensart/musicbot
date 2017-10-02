import click
import functools

from logging import debug, info, warning, error, critical
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

default_formats = ["mp3", "flac"]
filter_options = [
    click.option('--filter',       help='Filter file to load'),
    click.option('--limit',        help='Fetch a maximum limit of music'),
    click.option('--youtube',      help='Select musics with a youtube link', default=None, is_flag=True),
    click.option('--formats',      help='Select musics with file format, comma separated', default=','.join(default_formats)),
    click.option('--no-formats',   help='Filter musics without format, comma separated, can be "None" for empty string'),
    click.option('--keywords',     help='Select musics with keywords, comma separated, can be "None" for empty string'),
    click.option('--no-keywords',  help='Filter musics without keywords, comma separated, can be "None" for empty string'),
    click.option('--artists',      help='Select musics with artists, comma separated, can be "None" for empty string'),
    click.option('--no-artists',   help='Filter musics without artists, comma separated, can be "None" for empty string'),
    click.option('--albums',       help='Select musics with albums, comma separated, can be "None" for empty string'),
    click.option('--no-albums',    help='Filter musics without albums, comma separated, can be "None" for empty string'),
    click.option('--titles',       help='Select musics with titles, comma separated, can be "None" for empty string'),
    click.option('--no-titles',    help='Filter musics without titless, comma separated, can be "None" for empty string'),
    click.option('--genres',      help='Select musics with genres, comma separated, can be "None" for empty string'),
    click.option('--no-genres',    help='Filter musics without genres, comma separated, can be "None" for empty string'),
    click.option('--min-duration', help='Minimum duration filter (hours:minutes:seconds)'),
    click.option('--max-duration', help='Maximum duration filter (hours:minutes:seconds))'),
    click.option('--min-size',     help='Minimum file size filter (in bytes)'),
    click.option('--max-size',     help='Maximum file size filter (in bytes)'),
    click.option('--min-rating',   help='Minimum rating (between {default_min_rating} and {default_max_rating})'),
    click.option('--max-rating',   help='Maximum rating (between {default_min_rating} and {default_max_rating})')
]

def add_options(options):
    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func
    return _add_options

class Context(object):
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

pass_context = click.make_pass_decorator(Context, ensure=True)

class SubCommandLineInterface(click.MultiCommand):
    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(plugin_folder):
            if filename.endswith('.py'):
                rv.append(filename[:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        ns = {}
        fn = os.path.join(plugin_folder, name + '.py')
        with open(fn) as f:
            code = compile(f.read(), fn, 'exec')
            eval(code, ns, ns)
        return ns['cli']

