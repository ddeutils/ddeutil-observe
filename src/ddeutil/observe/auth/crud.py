from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..crud import BaseCRUD
from .models import User
from .schemas import UserSchema, UserSchemaCreateForm
from .securities import get_password_hash, verify_password


async def authenticate(
    session: Session,
    *,
    name: str,
    password: str,
) -> Optional[User]:
    if user := await User.get_by_name(session, name=name):
        return user if verify_password(password, user.hashed_password) else None
    else:
        return None


class CreateUser(BaseCRUD):
    async def by_form(self, user: UserSchemaCreateForm) -> UserSchema:
        # NOTE: Validate by username value. By default, this will validate
        # from database with unique constraint.
        _user = await User.get_by_name(self.async_session, user.name)
        print(_user)
        if _user:
            raise HTTPException(status_code=409)

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
        print(_user_create.__dict__)
        return UserSchema.model_validate(_user_create)
