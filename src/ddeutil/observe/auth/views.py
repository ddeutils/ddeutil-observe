# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi import status as st
from fastapi.responses import HTMLResponse, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from ..conf import config
from ..deps import get_async_session, get_templates
from .crud import UserCRUD, authenticate
from .deps import get_current_active_user
from .models import User
from .schemas import UserCreateForm, UserResetPassForm
from .securities import create_access_token

auth = APIRouter(prefix="/auth", tags=["auth"])


@auth.get("/register", response_class=HTMLResponse)
def register(
    request: Request,
    template: Jinja2Templates = Depends(get_templates),
):
    return template.TemplateResponse(
        request=request,
        name="auth/authenticate.html",
        context={"content": "register"},
    )


@auth.post("/register")
async def register(
    response: Response,
    form_user: Annotated[UserCreateForm, Form()],
    service: UserCRUD = Depends(UserCRUD),
):
    await service.create_by_form(form_user)
    response.headers["HX-Redirect"] = "/auth/login/"
    response.status_code = st.HTTP_307_TEMPORARY_REDIRECT
    return {}


@auth.get("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    templates: Jinja2Templates = Depends(get_templates),
):
    return templates.TemplateResponse(
        request=request,
        name="auth/authenticate.html",
        context={"request": request, "content": "login"},
    )


@auth.post("/login")
async def login(
    response: Response,
    session: AsyncSession = Depends(get_async_session),
    form_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm),
):
    user = await authenticate(
        session,
        name=form_data.username,
        password=form_data.password,
    )
    if user is None:
        response.headers["HX-Redirect"] = "/"
        response.status_code = st.HTTP_404_NOT_FOUND
        return {}

    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject={
            "sub": user.username,
            # NOTE: OAuth2 with scopes such as `["me"]`.
            "scopes": form_data.scopes,
        },
        expires_delta=access_token_expires,
    )
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        expires=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
    )
    # response.set_cookie(
    #     key="refresh_token",
    #     value=refresh_token,
    #     httponly=True,
    #     secure=True,
    #     samesite="Lax",
    #     max_age=max_age,
    # )
    response.headers["HX-Redirect"] = "/"
    response.status_code = st.HTTP_302_FOUND
    return {
        "access_token": access_token,
        "exp": access_token_expires,
    }


@auth.post("/change-password")
async def change_password(
    response: Response,
    form_data: Annotated[UserResetPassForm, Depends()],
    session: AsyncSession = Depends(get_async_session),
):
    user = await authenticate(
        session,
        name=form_data.username,
        password=form_data.old_password,
    )
    if user is None:
        raise HTTPException(
            status_code=st.HTTP_400_BAD_REQUEST,
            detail="User not found",
        )

    # if not verify_password(form_data.old_password, user.password):
    #     raise HTTPException(
    #         status_code=st.HTTP_400_BAD_REQUEST,
    #         detail="Invalid old password"
    #     )
    #
    # encrypted_password = get_hashed_password(form_data.new_password)
    # user.password = encrypted_password
    await session.commit()

    response.headers["HX-Redirect"] = "/auth/login"
    response.status_code = st.HTTP_307_TEMPORARY_REDIRECT
    return {"message": "Password changed successfully"}


@auth.post("/logout")
async def logout(
    response: Response,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    # token_record = db.query(models.TokenTable).all()
    # info = []
    # for record in token_record:
    #     print("record", record)
    #     if (datetime.utcnow() - record.created_date).days > 1:
    #         info.append(record.user_id)
    #
    # if info:
    #     existing_token = db.query(models.TokenTable).where(
    #         TokenTable.user_id.in_(info)).delete()
    #     db.commit()
    #
    # existing_token = db.query(models.TokenTable).filter(
    #     models.TokenTable.user_id == user_id,
    #     models.TokenTable.access_toke == token).first()
    #
    # if existing_token:
    #     existing_token.status = False
    #     db.add(existing_token)
    #     db.commit()
    #     db.refresh(existing_token)
    response.delete_cookie(
        key="access_token",
        httponly=True,
    )
    response.headers["HX-Redirect"] = "/"
    response.status_code = st.HTTP_302_FOUND
    return {"message": "Logout Successfully"}
