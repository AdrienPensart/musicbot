'''Timing helpers'''
import datetime
import functools
import inspect
import logging
import time
from typing import Any, Callable

logger = logging.getLogger(__name__)


def seconds_to_human(seconds: int) -> str:
    '''Human readable duration from seconds'''
    return str(datetime.timedelta(seconds=seconds))


def timeit(*wrapper_args: Any, **wrapper_kwargs: Any) -> Any:
    '''Function decorator to have time statistics'''
    from musicbot.object import MusicbotObject
    func = None
    if len(wrapper_args) == 1 and callable(wrapper_args[0]):
        func = wrapper_args[0]
    if func:
        always = False
        on_success = False
        on_config = True
    else:
        always = wrapper_kwargs.get('always', False)
        on_success = wrapper_kwargs.get('on_success', False)
        on_config = wrapper_kwargs.get('on_config', True)

    def real_timeit(func: Callable) -> Any:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.time()
            result = func(*args, **kwargs)
            for_human = seconds_to_human(int(time.time() - start))

            if MusicbotObject.config.info or MusicbotObject.config.debug:
                args_values = []
                argspec = inspect.getfullargspec(func)
                # go through each position based argument
                counter = 0
                if argspec.args and isinstance(argspec.args, list):
                    for arg in args:
                        # when you run past the formal positional arguments
                        try:
                            args_values.append(str(argspec.args[counter]) + " = " + str(arg))
                            counter += 1
                        except IndexError:
                            # then fallback to using the positional varargs name
                            if argspec.varargs:
                                varargsname = argspec.varargs
                                args_values.append("*" + varargsname + " = " + str(arg))

                # finally show the named varargs
                for k, v in kwargs.items():
                    args_values.append(k + " = " + str(v))

                args_values_str = '|'.join(args_values)
                timing = f'(timings) {func.__module__}.{func.__qualname__} ({args_values_str}): {for_human} | result = {result}'
            else:
                timing = f'(timings) {func.__module__}.{func.__qualname__} : {for_human}'
            if always or (on_success and result) or (on_config and MusicbotObject.config.timings):
                MusicbotObject.timing(timing)
            return result
        return wrapper
    return real_timeit(func) if func else real_timeit
