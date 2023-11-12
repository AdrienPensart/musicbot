import logging
import socket
import time
from pathlib import Path

from beartype import beartype
from click.testing import CliRunner
from pytest import fixture, skip

from musicbot import File, MusicDb, ScanFolders, syncify

from . import fixtures

logger = logging.getLogger(__name__)


@fixture
@beartype
def cli_runner() -> CliRunner:
    """Instance of `click.testing.CliRunner` with mix_stderr=False"""
    return CliRunner(mix_stderr=False)


@beartype
def wait_for_service(hostname: str, port: int, timeout: int = 60) -> bool:
    start_time = time.perf_counter()
    while True:
        try:
            with socket.create_connection((hostname, port), timeout=timeout):
                return True
        except OSError:
            time.sleep(0.01)
            if time.perf_counter() - start_time >= timeout:
                return False


@fixture(scope="session")
@beartype
def edgedb() -> str:
    # hostname = "127.0.0.1"
    # port = 5657
    # dsn = f"""edgedb://testuser:testpass@{hostname}:{port}"""
    hostname = "localhost"
    port = 10700
    dsn = "edgedb://edgedb:oB1IZfMVuSgzySmIYLobxt30@localhost:10700"
    if not wait_for_service(hostname, port):
        _ = skip(f"Timeout during wait for {dsn}")
    return dsn


@fixture(scope="session", autouse=True)
@syncify
@beartype
async def testmusics(edgedb: str) -> list[File]:
    musicdb = MusicDb.from_dsn(edgedb)
    _ = await musicdb.clean_musics()

    scan_folders = ScanFolders([Path(folder) for folder in fixtures.scan_folders])
    files = await musicdb.upsert_folders(scan_folders=scan_folders)
    assert files, "Empty music db"
    return files
