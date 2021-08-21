from typing import Collection, Iterable
import logging
import os
from musicbot.object import MusicbotObject
from musicbot.timing import timeit
from musicbot.music.file import File, supported_formats
from musicbot.music.helpers import find_files, filecount

logger = logging.getLogger(__name__)


@timeit
def genfiles(folders: Iterable[str]) -> Collection[File]:
    directories = [os.path.abspath(f) for f in folders]
    count = 0
    for directory in directories:
        subcount = filecount(directory, supported_formats)
        logger.info(f"{directory} : file count: {subcount}")
        count += subcount

    file_list = find_files(folders, supported_formats)
    music_files = list(file_list)
    files = []

    def worker(file):
        try:
            m = File(file[1], file[0])
            files.append(m)
        except KeyboardInterrupt as e:
            logger.error(f'interrupted : {e}')
            raise
        except OSError as e:
            logger.error(e)
    MusicbotObject.parallel(worker, music_files)
    return files
