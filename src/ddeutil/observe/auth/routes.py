from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..deps import get_async_session
from . import models
from .schemas import (
    UserSchema,
)

auth = APIRouter(prefix="/auth", tags=["api", "auth"])


@auth.get("/user/{name}", response_model=UserSchema)
async def get_user(
    name: str,
    session: AsyncSession = Depends(get_async_session),
):
    return await models.User.get_by_name(session, name=name)


@auth.get("/user", response_model=list[UserSchema])
async def get_users(db: AsyncSession = Depends(get_async_session)):
    _users = await models.User.get_all(db)
    return _users
