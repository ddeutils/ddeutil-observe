import asyncio
from collections.abc import Iterator
from contextlib import ExitStack
from pathlib import Path

import pytest
from ddeutil.observe.app import app as server
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

from .utils import initial_db

db_path: Path = Path(__file__).parent.parent / "observe.db"
db_path.unlink(missing_ok=True)
initial_db(db_path=db_path)


@pytest.fixture(autouse=True)
def app():
    with ExitStack():
        yield server


@pytest.fixture
def client(app):
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def setup_db() -> Iterator[None]:
    engine = create_engine(
        f"sqlite:///{Path(__file__).parent.parent / 'observe.db'}",
        connect_args={"check_same_thread": False},
    )

    yield

    conn = engine.connect()
    conn.execute("commit")
    try:
        conn.execute("drop database test")
    except SQLAlchemyError:
        pass
    conn.close()


def test_create_user(client):
    response = client.get("/home/")
    assert response.status_code == 200
    assert response.json() == []
