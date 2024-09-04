# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

import pathlib
from collections.abc import AsyncIterator, Iterator

from fastapi import Request
from fastapi.templating import Jinja2Templates
from jinja2 import ChoiceLoader, FileSystemLoader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from .db import AsyncSessionLocal, SessionLocal


def get_templates(request: Request) -> Jinja2Templates:
    """Dynamic multi-templating Jinja2 loader that support templates inside
    APIRouter.
    """
    choices: list[FileSystemLoader] = [FileSystemLoader("./templates")]
    if request.url.path != "/":
        route: str = request.url.path.strip("/").split("/")[0]
        route_path: pathlib.Path = (
            pathlib.Path(__file__).parent / f"routes/{route}/templates"
        )
        if route_path.exists():
            choices.insert(0, FileSystemLoader(route_path))

    return Jinja2Templates(
        directory="templates",
        loader=ChoiceLoader(choices),
    )


def get_session() -> Iterator[Session]:
    """Return the database local session instance."""
    session: Session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


async def get_async_session() -> AsyncIterator[AsyncSession]:
    """Return the database local async session instance."""
    session: AsyncSession = AsyncSessionLocal()
    try:
        yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
