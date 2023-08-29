import logging
import socket
import time
from pathlib import Path

from beartype import beartype
from click.testing import CliRunner
from pytest import fixture

from musicbot.file import File
from musicbot.folders import Folders
from musicbot.helpers import syncify
from musicbot.musicdb import MusicDb

from . import fixtures

logger = logging.getLogger(__name__)


@fixture
@beartype
def cli_runner() -> CliRunner:
    """Instance of `click.testing.CliRunner` with mix_stderr=False"""
    return CliRunner(mix_stderr=False)


@beartype
def wait_for_service(hostname: str, port: int, timeout: int = 60) -> None:
    start_time = time.perf_counter()
    while True:
        try:
            with socket.create_connection((hostname, port), timeout=timeout):
                break
        except OSError as e:
            time.sleep(0.01)
            if time.perf_counter() - start_time >= timeout:
                msg = f"Waited too long for {hostname}:{port} to start accepting connections."
                raise TimeoutError(msg) from e


@fixture(scope="session")
@beartype
def edgedb() -> str:
    hostname = "127.0.0.1"
    port = 15656
    dsn = f"""edgedb://edgedb:musicbot@{hostname}:{port}"""
    wait_for_service(hostname, port)
    return dsn


@fixture(scope="session", autouse=True)
@syncify
@beartype
async def testmusics(edgedb: str) -> list[File]:
    musicdb = MusicDb.from_dsn(edgedb)
    await musicdb.clean_musics()

    folders = Folders([Path(folder) for folder in fixtures.folders])
    files = await musicdb.upsert_folders(folders=folders)
    assert files, "Empty music db"
    return files
