from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..deps import get_async_session
from .models import User as UserModel
from .schemas import (
    UserSchema,
    UserSchemaCreate,
)

auth = APIRouter(
    prefix="/auth",
)


@auth.get("/user/{iden}", response_model=UserSchema)
async def get_user(iden: str, db: AsyncSession = Depends(get_async_session)):
    user = await UserModel.get(db, iden)
    return user


@auth.get("/user", response_model=list[UserSchema])
async def get_users(db: AsyncSession = Depends(get_async_session)):
    _users = await UserModel.get_all(db)
    return _users


@auth.post("/user", response_model=UserSchema)
async def create_user(
    user: UserSchemaCreate, db: AsyncSession = Depends(get_async_session)
):
    user = await UserModel.create(db, **user.dict())
    return user
