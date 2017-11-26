# -*- coding: utf-8 -*-
import asyncio
import time
import uvloop
from functools import wraps
from logging import debug, info
from .config import config

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


def timeit(f):
    async def process(f, *args, **params):
        if asyncio.iscoroutinefunction(f):
            return await f(*args, **params)
        else:
            return f(*args, **params)

    @wraps(f)
    async def helper(*args, **params):
        start = time.time()
        result = await process(f, *args, **params)
        # Test normal function route...
        # result = await process(lambda *a, **p: print(*a, **p), *args, **params)
        debug('{}: {}'.format(f.__name__, time.time() - start))
        return result

    return helper


def coro(f):
    f = asyncio.coroutine(f)

    @wraps(f)
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(f(*args, **kwargs))
    return wrapper


def drier(f):
    @wraps(f)
    async def wrapper(*args, **kwargs):
        if config.dry:
            args = [str(a) for a in args] + ["%s=%s" % (k, v) for (k, v) in kwargs.items()]
            info('DRY RUN: {}({})'.format(f.__name__, ','.join(args)))
            await asyncio.sleep(0)
        else:
            return await f(*args, **kwargs)
    return wrapper
