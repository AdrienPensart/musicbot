from typing import List
import logging
import sys
import signal
import os
import concurrent.futures as cf
from threading import Lock
import click
import progressbar  # type: ignore
from musicbot.defaults import DEFAULT_CONCURRENCY
from musicbot.config import DEFAULT_QUIET, Config

logger = logging.getLogger(__name__)


class MusicbotObject:
    print_lock = Lock()
    is_tty = sys.stderr.isatty()
    show_warn: bool = True
    show_err: bool = True
    show_tip: bool = True
    show_echo: bool = True
    show_timing: bool = True
    show_header: bool = True
    show_success: bool = True
    already_printed: List[str] = []
    config = Config()
    dry = False

    @classmethod
    def timing(cls, message, **options):
        '''Print timing informations'''
        if cls.show_timing:
            cls.echo(message, fg="magenta", bold=True, **options)

    @classmethod
    def header(cls, message, **options):
        '''Print information about sequential executions'''
        if cls.show_header:
            cls.echo(message, fg='cyan', bold=True, **options)

    @classmethod
    def err(cls, message, **options):
        '''Print error to the user'''
        if cls.show_err:
            cls.echo(message, fg='red', **options)

    @classmethod
    def warn(cls, message, **options):
        '''Print warning to the user'''
        if cls.show_warn:
            cls.echo(message, fg='yellow', **options)

    @classmethod
    def tip(cls, message, **options):
        '''Give a useful tip to the user'''
        if cls.show_tip and message not in cls.already_printed:
            cls.echo(message, fg='bright_blue', **options)
            cls.already_printed.append(message)

    @classmethod
    def success(cls, message, **options):
        '''Print a successful operation to the user'''
        if cls.show_success:
            cls.echo(message, fg='green', **options)

    @classmethod
    def echo(cls, message, quiet=DEFAULT_QUIET, file=None, end='\n', flush=True, **secho_options):
        '''Print a normal message to the user'''
        file = file if file is not None else sys.stderr
        if not quiet and not cls.config.quiet:
            if cls.config.color:
                final_message = click.style(f'{message}', **secho_options)
            else:
                final_message = f'{message}'
            with cls.print_lock:
                print(final_message, file=file, flush=flush, end=end)

    @classmethod
    def progressbar(cls, quiet=DEFAULT_QUIET, redirect_stderr=True, redirect_stdout=True, **pbar_options):
        if quiet or cls.config.quiet:
            pbar = progressbar.NullBar
        else:
            pbar = progressbar.ProgressBar
        return pbar(redirect_stderr=redirect_stderr, redirect_stdout=redirect_stdout, **pbar_options)

    @classmethod
    def parallel(cls, worker, items, quiet=DEFAULT_QUIET, concurrency=DEFAULT_CONCURRENCY, **pbar_options):
        with cls.progressbar(max_value=len(items), quiet=quiet, redirect_stderr=True, redirect_stdout=True, **pbar_options) as pbar, \
             cf.ThreadPoolExecutor(max_workers=concurrency) as executor:
            try:
                def update_pbar(_):
                    try:
                        pbar.value += 1
                        pbar.update()
                    except KeyboardInterrupt as e:
                        logger.error(f"interrupted : {e}")
                        while True:
                            os.kill(os.getpid(), signal.SIGKILL)
                            os.killpg(os.getpid(), signal.SIGKILL)
                futures = []
                for item in items:
                    future = executor.submit(worker, item)
                    future.add_done_callback(update_pbar)
                    futures.append(future)
                cf.wait(futures)
                return [future.result() for future in futures if future.result() is not None]
            except KeyboardInterrupt as e:
                logger.error(f"interrupted : {e}")
                if 'pytest' in sys.modules:
                    raise e
                while True:
                    os.kill(os.getpid(), signal.SIGKILL)
                    os.killpg(os.getpid(), signal.SIGKILL)
