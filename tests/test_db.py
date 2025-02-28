from pathlib import Path

import pytest
from ddeutil.observe.db import Base
from sqlalchemy import create_engine


@pytest.fixture(scope="module")
def engine(db_pointer: Path):
    engine = create_engine(
        f"sqlite:///{db_pointer}",
        connect_args={"check_same_thread": False},
    )

    Base.metadata.create_all(engine)

    return engine


@pytest.fixture(scope="module")
def db_session(engine):

    yield


def test_model_role(db_session): ...
