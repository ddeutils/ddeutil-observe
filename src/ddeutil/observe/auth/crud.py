# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from typing import Optional

from fastapi import HTTPException
from fastapi import status as st
from sqlalchemy.orm import Session

from ..crud import BaseCRUD
from .models import User
from .schemas import UserSchema, UserSchemaCreateForm
from .securities import get_password_hash, verify_password


async def authenticate(
    session: Session,
    name: str,
    password: str,
) -> Optional[User]:
    if user := await User.get_by_name(session, name=name):
        return (
            user if verify_password(password, user.hashed_password) else False
        )
    return False


class CreateUser(BaseCRUD):
    async def by_form(self, user: UserSchemaCreateForm) -> UserSchema:
        # NOTE: Validate by username value. By default, this will validate
        # from database with unique constraint.

        if await User.get_by_name(self.async_session, user.name):
            raise HTTPException(status_code=st.HTTP_409_CONFLICT)

        hashed_password = get_password_hash(user.password)
        _user_create: User = User(
            email=user.email, name=user.name, hashed_password=hashed_password
        )
        self.async_session.add(_user_create)

        # `flush`, communicates a series of operations to the database
        # (insert, update, delete). The database maintains them as pending
        # operations in a transaction. The changes aren't persisted
        # permanently to disk, or visible to other transactions until the
        # database receives a COMMIT for the current transaction (which is
        # what session.commit() does).
        # ---
        # docs: https://stackoverflow.com/questions/4201455/ -
        #   sqlalchemy-whats-the-difference-between-flush-and-commit
        await self.async_session.flush()

        # # `commit`, commits (persists) those changes to the database.
        await self.async_session.commit()

        # NOTE: persisted some changes for an object to the database and
        # need to use this updated object within the same method.
        await self.async_session.refresh(_user_create)
        return UserSchema.model_validate(_user_create)
