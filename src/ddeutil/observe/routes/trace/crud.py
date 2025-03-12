# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ...crud import BaseCRUD
from .. import models as md

logger = logging.getLogger("uvicorn.error")


class TraceCRUD(BaseCRUD):

    async def list(
        self,
        skip: int = 0,
        limit: int = 1000,
    ) -> list[md.Trace]:
        for row in (
            await (
                await self.async_session.stream(
                    select(md.Trace)
                    .options(selectinload(md.Trace.meta))
                    .offset(skip)
                    .limit(limit)
                )
            )
            .scalars()
            .all()
        ):
            yield row

    async def get(
        self,
        run_id: str,
        include_meta: bool = True,
    ) -> md.Trace:
        stmt = select(md.Workflow)
        if include_meta:
            stmt = stmt.options(selectinload(md.Trace.meta))
        return (
            await self.async_session.execute(
                stmt.filter(md.Trace.run_id == run_id).limit(1)
            )
        ).first()
