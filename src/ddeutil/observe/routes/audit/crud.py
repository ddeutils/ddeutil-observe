# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

import logging
from datetime import datetime

from sqlalchemy import select

from ...crud import BaseCRUD
from .. import models as md
from .schemas import AuditCreate

logger = logging.getLogger("uvicorn.error")


class AuditCRUD(BaseCRUD):

    async def get(
        self,
        audit: datetime,
    ) -> md.Audit:
        return (
            await self.async_session.execute(
                select(md.Audit).filter(md.Audit.release == audit).limit(1)
            )
        ).first()

    async def create_with_trace(
        self,
        workflow_id: int,
        audit_trace: AuditCreate,
    ) -> md.Audit:
        db_release = md.Audit(
            release=audit_trace.release,
            workflow_id=workflow_id,
        )
        self.async_session.add(db_release)
        await self.async_session.flush()
        await self.async_session.commit()
        await self.async_session.refresh(db_release)

        for log in audit_trace.logs:
            db_log = md.Trace(
                run_id=log.run_id,
                context=log.context,
                release_id=db_release.id,
            )
            self.async_session.add(db_log)
            await self.async_session.flush()
            await self.async_session.commit()
            await self.async_session.refresh(db_log)
        return db_release
