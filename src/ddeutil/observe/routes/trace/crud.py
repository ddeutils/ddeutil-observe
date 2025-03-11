# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from sqlalchemy import select

from ...crud import BaseCRUD
from ...utils import get_logger
from .. import models as md

logger = get_logger("ddeutil.observe")


class TraceCRUD(BaseCRUD):

    async def get_log(self, run_id: str) -> md.Trace:
        return (
            await self.async_session.execute(
                select(md.Trace).filter(md.Trace.run_id == run_id).limit(1)
            )
        ).first()
