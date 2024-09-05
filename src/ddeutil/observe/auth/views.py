# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends, Request
from fastapi import status as st
from fastapi.responses import HTMLResponse, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from ..conf import config
from ..deps import get_async_session, get_templates
from .crud import CreateUser, authenticate
from .schemas import UserSchemaCreateForm
from .securities import create_access_token

auth = APIRouter(prefix="/auth", tags=["auth"])


@auth.get("/register/", response_class=HTMLResponse)
def register(
    request: Request,
    template: Jinja2Templates = Depends(get_templates),
):
    return template.TemplateResponse(
        request=request,
        name="auth/index.html",
        context={"content": "register"},
    )


@auth.post("/register/")
async def register(
    response: Response,
    user: UserSchemaCreateForm = Depends(UserSchemaCreateForm.as_form),
    service: CreateUser = Depends(CreateUser),
):
    await service.by_form(user)
    response.headers["HX-Redirect"] = "/auth/login/"
    response.status_code = st.HTTP_303_SEE_OTHER
    return {}


@auth.get("/login/", response_class=HTMLResponse)
async def login(
    request: Request,
    templates: Jinja2Templates = Depends(get_templates),
):
    return templates.TemplateResponse(
        request=request,
        name="auth/index.html",
        context={"request": request, "content": "login"},
    )


@auth.post("/login/")
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
            "sub": user.name,
            # NOTE: OAuth2 with scopes.
            "scopes": form_data.scopes,
        },
        expires_delta=access_token_expires,
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        expires=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    response.headers["HX-Redirect"] = "/"
    response.status_code = st.HTTP_302_FOUND
    return {}
