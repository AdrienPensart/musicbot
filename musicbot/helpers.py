import time
import os
import logging
import string
import random
import functools
import click
import click_spinner
from click_didyoumean import DYMGroup
from click_aliases import ClickAliasedGroup
from tqdm import tqdm
from .config import config
from .lib import seconds_to_human, find_files, filecount
from .music.file import File, supported_formats

logger = logging.getLogger(__name__)

MB_CONCURRENCY = 'MB_CONCURRENCY'
DEFAULT_MB_CONCURRENCY = 8
concurrency_options = [click.option('--concurrency', envvar=MB_CONCURRENCY, help='Number of coroutines', default=DEFAULT_MB_CONCURRENCY, show_default=True)]

DEFAULT_DRY = False
MB_DRY = 'MB_DRY'
dry_option = [click.option('--dry', help='Take no real action', envvar=MB_DRY, default=DEFAULT_DRY, is_flag=True, show_default=True)]


logger = logging.getLogger(__name__)


def random_password(size=8):
    alphabet = string.ascii_letters + string.digits
    return ''.join(random.choice(alphabet) for i in range(size))


class GroupWithHelp(DYMGroup, ClickAliasedGroup):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        @click.command('help')
        @click.argument('command', nargs=-1)
        @click.pass_context
        def _help(ctx, command):
            '''Print help'''
            if command:
                argument = command[0]
                c = self.get_command(ctx, argument)
                print(c.get_help(ctx))
            else:
                print(ctx.parent.get_help())
        self.add_command(_help)


def timeit(f):
    @functools.wraps(f)
    def wrapper(*args, **params):
        start = time.time()
        result = f(*args, **params)
        for_human = seconds_to_human(time.time() - start)
        if config.timings:
            logger.info('TIMINGS %s: %s', f.__name__, for_human)
        return result
    return wrapper


def add_options(options):
    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func
    return _add_options


def config_string(envvar, configkey, required, ctx, param, value):
    if not value:
        logger.info("Try loading with envvar %s", envvar)
        value = os.getenv(envvar, None)
    if not value:
        logger.info("Try loading with config key %s", configkey)
        value = config.configfile['DEFAULT'].get(configkey, None)
    if not value:
        if required:
            raise click.BadParameter('or missing env {} / config {} in {}'.format(envvar, configkey, config.config), ctx, param)
    logger.info("Value loaded: %s", value)
    ctx.params[param.name] = value
    return ctx.params[param.name]


@timeit
def genfiles(folders):
    with click_spinner.spinner(disable=config.quiet):
        count = 0
        directories = [os.path.abspath(f) for f in folders]
        for d in directories:
            count += filecount(d, supported_formats)
        logger.info("File count: %s", count)
    files = []
    with tqdm(total=count, desc="Music listing", leave=False, disable=config.quiet) as pbar:
        file_list = find_files(folders, supported_formats)
        music_files = list(file_list)
        for f in music_files:
            try:
                m = File(f[1], f[0])
                files.append(m)
                pbar.update(1)
            except OSError as e:
                logger.error(e)
    return files
