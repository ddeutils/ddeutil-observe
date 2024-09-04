from collections.abc import Iterator
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

from .utils import initial_db

db_path: Path = Path(__file__).parent.parent / "observe.db"
db_path.unlink(missing_ok=True)
initial_db(db_path=db_path)


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
