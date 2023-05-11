import asyncio
import concurrent.futures as cf
import dataclasses
import io
import logging
import os
import signal
import sys
import threading
import traceback
from collections.abc import Callable, Collection, Coroutine, Iterable
from datetime import datetime
from functools import cache, partial, wraps
from typing import IO, Any, NoReturn, Sequence, ParamSpec, TypeVar

import attr
import click
import orjson
import requests
import rich
from beartype import beartype
from progressbar import NullBar, ProgressBar  # type: ignore
from requests.structures import CaseInsensitiveDict
from rich.console import Console
from rich.table import Table

from musicbot.config import DEFAULT_QUIET, Config
from musicbot.defaults import DEFAULT_THREADS
from musicbot.one_way_bool import OneWayBool

logger = logging.getLogger(__name__)


def default_encoder(data: Any) -> Any:
    """Encode in json structure which cannot"""
    if isinstance(data, (frozenset, set)):
        return list(data)
    if dataclasses.is_dataclass(data):
        return dataclasses.asdict(data)
    if isinstance(data, CaseInsensitiveDict):
        return dict(data)
    if attr.has(data.__class__):
        return attr.asdict(data)
    raise TypeError(f"Unable to encode {data}")


@cache
@beartype
def public_ip(timeout: int = 5) -> str | None:
    try:
        # return requests.get("https://api.ipify.org", timeout=timeout).text
        return requests.head('https://www.wikipedia.org', timeout=timeout).headers['X-Client-IP']
    except Exception as error:
        MusicbotObject.err("Unable to detect Public IP", error=error)
    return None


T_Retval = TypeVar("T_Retval")
T_ParamSpec = ParamSpec("T_ParamSpec")
T = TypeVar("T")


class MusicbotObject:
    print_lock = threading.Lock()
    is_tty = sys.stderr.isatty()
    console = Console()
    show_warn: bool = True
    show_err: bool = True
    show_tip: bool = True
    show_echo: bool = True
    show_success: bool = True
    already_printed: list[str] = []
    config = Config(quiet=False)
    dry = OneWayBool("dry", default=False)
    _public_ip: str | None = None

    def __repr__(self) -> str:
        return "[DRY]" if self.dry else "[DOING]"

    @classmethod
    def syncify(
        cls,
        async_function: Callable[T_ParamSpec, Coroutine[Any, Any, T_Retval]],
    ) -> Callable[T_ParamSpec, T_Retval]:
        """Run an async task"""

        @wraps(async_function)
        def wrapper(*args: T_ParamSpec.args, **kwargs: T_ParamSpec.kwargs) -> T_Retval:
            partial_f = partial(async_function, *args, **kwargs)
            with asyncio.Runner() as runner:
                return runner.run(partial_f())

        return wrapper

    @classmethod
    def public_ip(cls) -> str | None:
        return public_ip()

    @staticmethod
    def is_dev() -> bool:
        """Do we execute Unity from a dev folder?"""
        if "poetry" in os.environ.get("VIRTUAL_ENV", ""):
            return True
        return bool(sys.flags.dev_mode) or "main.py" in sys.argv[0]

    @staticmethod
    def is_test() -> bool:
        """Are we in a test session ?"""
        return "pytest" in sys.modules

    @classmethod
    def is_prod(cls) -> bool:
        """Are we executing the prod version?"""
        return not cls.is_dev() and not cls.is_test()

    @classmethod
    def err(
        cls,
        message: Any,
        file: IO | None = None,
        error: Exception | None = None,
        **options: Any,
    ) -> None:
        """Print error to the user"""
        file = file if file is not None else sys.stderr
        if error is not None:
            final_message = f"{message} : {error}"
        else:
            final_message = message
        if error is not None and not cls.is_prod():
            traceback.print_stack(file=file)
            logger.exception(error)
        if cls.show_err:
            cls.echo(final_message, fg="red", **options)

    @classmethod
    def warn(cls, message: Any, **options: Any) -> None:
        """Print warning to the user"""
        if cls.show_warn:
            cls.echo(message, fg="yellow", **options)

    @classmethod
    def tip(cls, message: Any, only_once: bool = True, **options: Any) -> None:
        """Give a useful tip to the user"""
        if cls.show_tip and message not in cls.already_printed:
            cls.echo(message, fg="bright_blue", only_once=only_once, **options)
            cls.already_printed.append(message)

    @classmethod
    def success(cls, message: Any, **options: Any) -> None:
        """Print a successful operation to the user"""
        if cls.show_success:
            cls.echo(message, fg="green", **options)

    @classmethod
    def echo(
        cls,
        message: Any,
        quiet: bool = DEFAULT_QUIET,
        file: IO | None = None,
        end: str = "\n",
        flush: bool = True,
        only_once: bool = False,
        **kwargs: Any,
    ) -> None:
        """Print a normal message to the user"""
        file = file if file is not None else sys.stderr
        timing = ""
        if cls.config.debug:
            now = datetime.now()
            timing = now.strftime("%Y-%d-%d %H:%M:%S | ")

        if not quiet and cls.show_echo and not cls.config.quiet:
            if cls.config.color:
                final_message = click.style(f"\r{timing}{message}\033[K", **kwargs)
            else:
                final_message = f"\r{message}\033[K"
            with cls.print_lock:
                if only_once:
                    if message in cls.already_printed:
                        return
                    cls.already_printed.append(message)
                print(final_message, file=file, flush=flush, end=end)
                # if cls.config.log:
                #     logger.info(message)

    @classmethod
    def progressbar(
        cls,
        quiet: bool = DEFAULT_QUIET,
        desc: str | None = None,
        redirect_stderr: bool = True,
        redirect_stdout: bool = True,
        term_width: int | None = 150,
        **kwargs: Any,
    ) -> NullBar | ProgressBar:
        if desc:
            desc += " : "
        pbar = NullBar if (quiet or cls.config.quiet) else ProgressBar
        new_bar = pbar(
            prefix=desc,
            redirect_stderr=redirect_stderr,
            redirect_stdout=redirect_stdout,
            term_width=term_width,
            **kwargs,
        )
        if cls.is_prod():
            _ = new_bar.update()
        return new_bar

    @classmethod
    def parallel_gather(
        cls,
        worker: Callable,
        items: Sequence,
        *args: Any,
        quiet: bool = DEFAULT_QUIET,
        desc: str | None = None,
        limit: int | None = None,
        threads: int | None = None,
        **kwargs: Any,
    ) -> list[Any]:
        threads = threads if threads not in (None, 0) else DEFAULT_THREADS
        quiet = len(items) <= 1 or quiet
        results: list[Any] = []
        if desc and (cls.is_dev() or cls.config.info or cls.config.debug):
            desc += f" ({threads} threads)"
        if threads == 1:
            with cls.progressbar(
                max_value=len(items),
                quiet=quiet,
                redirect_stderr=True,
                redirect_stdout=True,
                desc=desc,
                **kwargs,
            ) as pbar:
                results = []
                for item in items:
                    try:
                        result = worker(item)
                        if result is not None:
                            results.append(result)
                    finally:
                        pbar.value += 1
                        _ = pbar.update()
        else:
            with (
                cls.progressbar(
                    max_value=len(items),
                    quiet=quiet,
                    redirect_stderr=True,
                    redirect_stdout=True,
                    desc=desc,
                    **kwargs,
                ) as pbar,
                cf.ThreadPoolExecutor(max_workers=threads) as executor,
            ):
                try:

                    def update_pbar(_: Any) -> None:
                        try:
                            pbar.value += 1
                            _ = pbar.update()
                        except KeyboardInterrupt as e:
                            logger.error(f"interrupted : {e}")
                            while True:
                                os.kill(os.getpid(), signal.SIGKILL)
                                os.killpg(os.getpid(), signal.SIGKILL)

                    futures = []
                    for item in items:
                        future = executor.submit(worker, item, *args)
                        future.add_done_callback(update_pbar)
                        futures.append(future)
                    _, _ = cf.wait(futures)
                    return [future.result() for future in futures if future.result() is not None]
                except KeyboardInterrupt as e:
                    if cls.is_test():
                        raise e
                    cls.fast_kill()
        return results[:limit]

    @classmethod
    async def async_gather(
        cls,
        worker: Callable,
        items: Collection[Any],
        quiet: bool = False,
        desc: str | None = None,
        limit: int | None = None,
        merge: bool = False,
        return_exceptions: bool = False,
        **kwargs: Any,
    ) -> list[Any]:
        """
        A version of asyncio.gather that runs on the internal event loop
        """
        quiet = len(items) <= 1 or quiet
        if desc:
            desc += " (async)"
        with cls.progressbar(max_value=len(items), quiet=quiet, desc=desc, **kwargs) as pbar:
            try:

                async def _worker(worker_item: Any) -> Any:
                    try:
                        return await worker(worker_item)
                    finally:
                        pbar.value += 1
                        _ = pbar.update()

                futures = []
                for future_item in items:
                    future = _worker(future_item)
                    futures.append(future)

                results = await asyncio.gather(*futures, return_exceptions=return_exceptions)
                results = [result for result in results if result is not None]
                if not merge:
                    return results[:limit]

                final_results = []
                for sublist in results:
                    if isinstance(sublist, Iterable):
                        final_results.extend([item for item in sublist if item is not None])
            except KeyboardInterrupt as e:
                if cls.is_test():
                    raise e
                cls.fast_kill()
        return final_results[:limit]

    @classmethod
    def fast_kill(cls) -> NoReturn:  # pylint: disable=unused-argument
        """We don't do anything silly in musicbot, like open or writing files, etc
        so let's hard kill ourself to avoid multiple ctrl+c by user
        if a thread received the SIGKILL, it may kill the process,
        so we send them in continue until it reaches the main thread"""
        cls.err("interrupted, fast-killing process", only_once=True)
        while True:
            os.kill(os.getpid(), signal.SIGKILL)
            os.killpg(os.getpid(), signal.SIGKILL)

    @classmethod
    def print_table(cls, table: Table, file: IO | None = None) -> None:
        """Print rich table"""
        if file is not None:
            console = Console(file=io.StringIO(), width=300)
            console.print(table)
            output = console.file.getvalue()  # type: ignore  # pylint: disable=no-member
            print(output, file=file)
            return

        with cls.print_lock:
            print("\r\033[K", end="")
            cls.console.print(table)

    @classmethod
    def print_json(
        cls,
        data: Any,
        file: IO | None = None,
        option: int | None = orjson.OPT_INDENT_2 | orjson.OPT_SORT_KEYS | orjson.OPT_NON_STR_KEYS,  # pylint: disable=maybe-no-member
        default: Callable | None = default_encoder,
    ) -> None:
        """Print highlighted json to stdout depending if we are in a TTY"""
        file = file if file is not None else sys.stdout
        if (encoded := cls.dumps_json(data, option=option, default=default)) is None:
            return None
        if file.isatty():
            decoded = cls.loads_json(encoded)
            rich.print_json(
                data=decoded,
                highlight=cls.config.color,
                indent=2,
            )
        else:
            print(encoded, file=file)
        return None

    @classmethod
    def dumps_json(
        cls,
        data: Any,
        option: int | None = orjson.OPT_INDENT_2 | orjson.OPT_SORT_KEYS | orjson.OPT_NON_STR_KEYS,  # pylint: disable=maybe-no-member
        default: Callable | None = default_encoder,
        **kwargs: Any,
    ) -> str | None:
        """dumps json using global library"""
        try:
            return orjson.dumps(data, option=option, default=default, **kwargs).decode("utf-8")  # pylint: disable=maybe-no-member
        except orjson.JSONEncodeError as error:  # pylint: disable=maybe-no-member
            cls.err("Unable to encode json", error=error)
            logger.debug(data)
        return None

    @classmethod
    def loads_json(cls, data: bytes | bytearray | memoryview | str) -> Any | None:
        """loads json using global library"""
        try:
            return orjson.loads(data)  # pylint: disable=maybe-no-member
        except orjson.JSONDecodeError as error:  # pylint: disable=maybe-no-member
            cls.err("Unable to decode json", error=error)
            logger.debug(data)
        return None
