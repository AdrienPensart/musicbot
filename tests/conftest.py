# type: ignore
import logging
import socket
import time
from pathlib import Path

import pytest

from musicbot.folders import Folders
from musicbot.musicdb import MusicDb

from . import fixtures

logger = logging.getLogger(__name__)

pytest_plugins = ["docker_compose"]


def wait_for_service(service, timeout=60):
    start_time = time.perf_counter()
    while True:
        try:
            with socket.create_connection((service.hostname, service.host_port), timeout=timeout):
                break
        except OSError as e:
            time.sleep(0.01)
            if time.perf_counter() - start_time >= timeout:
                raise TimeoutError(f"Waited too long for the port {service.host_port} on host {service.hostname} to start accepting connections.") from e


@pytest.fixture(scope="session")
def edgedb(session_scoped_container_getter):
    service = session_scoped_container_getter.get("edgedb").network_info[0]
    dsn = f"""edgedb://edgedb:musicbot@{service.hostname}:{service.host_port}"""
    wait_for_service(service)
    return dsn


@pytest.fixture(scope="session", autouse=True)
def testmusics(edgedb):
    musicdb = MusicDb.from_dsn(edgedb)
    musicdb.sync_clean_musics()
    folders = Folders([Path(folder) for folder in fixtures.folders])
    files = musicdb.sync_upsert_folders(folders=folders)
    assert files, "Empty music db"
    yield files
    musicdb.sync_clean_musics()
