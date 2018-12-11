import asyncio
import time
import uvloop
import click
import logging
import string
import random
import functools
from click_didyoumean import DYMGroup
from .config import config
from .lib import seconds_to_human

logger = logging.getLogger(__name__)

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

DEFAULT_MB_CONCURRENCY = 8
concurrency_options = [
    click.option('--concurrency', envvar='MB_CONCURRENCY', help='Number of coroutines', default=DEFAULT_MB_CONCURRENCY, show_default=True),
]


def random_password(size=8):
    alphabet = string.ascii_letters + string.digits
    return ''.join(random.choice(alphabet) for i in range(size))


class GroupWithHelp(DYMGroup):
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


async def process(f, *args, **params):
    if asyncio.iscoroutinefunction(f):
        return await f(*args, **params)
    return f(*args, **params)


def timeit(f):
    @functools.wraps(f)
    def wrapper(*args, **params):
        start = time.time()
        result = f(*args, **params)
        for_human = seconds_to_human(time.time() - start)
        if config.timings:
            logger.info('TIMINGS %s: %s', f.__name__, for_human)
        return result

    @functools.wraps(f)
    async def awrapper(*args, **params):
        start = time.time()
        result = await process(f, *args, **params)
        for_human = seconds_to_human(time.time() - start)
        if config.timings:
            logger.info('TIMINGS %s: %s', f.__name__, for_human)
        return result

    if asyncio.iscoroutinefunction(f):
        return awrapper
    return wrapper


def add_options(options):
    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func
    return _add_options


def coro(f):
    f = asyncio.coroutine(f)

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(f(*args, **kwargs))
    return wrapper


def drier(f):
    @functools.wraps(f)
    async def wrapper(*args, **kwargs):
        if config.dry:
            args = [str(a) for a in args] + ["%s=%s" % (k, v) for (k, v) in kwargs.items()]
            logger.info('DRY RUN: %s(%s)', f.__name__, ','.join(args))
            await asyncio.sleep(0)
        else:
            return await process(f, *args, **kwargs)
    return wrapper
