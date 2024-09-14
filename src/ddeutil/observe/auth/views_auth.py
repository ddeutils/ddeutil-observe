# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Annotated, Union

from fastapi import APIRouter, Depends, Form, Request
from fastapi import status as st
from fastapi.responses import HTMLResponse, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from ..conf import config
from ..deps import get_async_session, get_templates
from .crud import TokenCRUD, UserCRUD, authenticate
from .deps import get_current_active_user
from .models import User
from .schemas import (
    TokenRefresh,
    TokenRefreshCreate,
    UserCreateForm,
    UserResetPassForm,
    UserScopeForm,
)
from .securities import create_access_token, create_refresh_token

auth = APIRouter(prefix="/auth", tags=["auth", "frontend"])


@auth.get("/register")
def register(
    request: Request,
    template: Jinja2Templates = Depends(get_templates),
) -> HTMLResponse:
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
    """Register information of user to this application for able to access any
    routes.
    """
    await service.create_by_form(form_user)
    response.headers["HX-Redirect"] = "/auth/login/"
    response.status_code = st.HTTP_307_TEMPORARY_REDIRECT
    return {}


@auth.get("/login")
async def login(
    request: Request,
    templates: Jinja2Templates = Depends(get_templates),
) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="auth/authenticate.html",
        context={"request": request, "content": "login"},
    )


@auth.post("/login")
async def login(
    response: Response,
    session: AsyncSession = Depends(get_async_session),
    form_scopes: UserScopeForm = Depends(UserScopeForm.as_form),
    form_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm),
    service: TokenCRUD = Depends(TokenCRUD),
):
    user: Union[User, bool] = await authenticate(
        session,
        name=form_data.username,
        password=form_data.password,
    )
    if not user:
        response.headers["HX-Redirect"] = "/auth/register"
        response.status_code = st.HTTP_404_NOT_FOUND
        return {}

    # NOTE: OAuth2 with scopes such as `["me", ...]`.
    access_token = create_access_token(
        subject={
            "sub": user.username,
            "scopes": form_scopes.scopes,
        },
    )
    refresh_token = create_refresh_token(
        subject={
            "sub": user.username,
            "scopes": form_scopes.scopes,
        },
    )

    # NOTE: Set cookies for access token and refresh token.
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        expires=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="Lax",
        max_age=config.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
    )

    await service.create(
        TokenRefreshCreate(
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=user.id,
            expires_at=(
                datetime.now()
                + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
            ),
        )
    )

    response.headers["HX-Redirect"] = "/"
    response.status_code = st.HTTP_302_FOUND
    return {
        "access_token": access_token,
        "exp": config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "token_type": "Bearer",
    }


@auth.get("/change-password")
async def change_password(
    request: Request,
    templates: Jinja2Templates = Depends(get_templates),
) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="auth/authenticate.html",
        context={"request": request, "content": "change-password"},
    )


@auth.post("/change-password")
async def change_password(
    response: Response,
    form_data: Annotated[UserResetPassForm, Depends()],
    service: UserCRUD = Depends(UserCRUD),
):
    await service.change_password(form_data)

    response.headers["HX-Redirect"] = "/auth/login"
    response.status_code = st.HTTP_307_TEMPORARY_REDIRECT
    return {"message": "Password changed successfully"}


@auth.post("/logout")
async def logout(
    request: Request,
    response: Response,
    user: User = Depends(get_current_active_user),
    service: TokenCRUD = Depends(TokenCRUD),
):
    await service.retention_by_user(user.id)

    db_tokens = []
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        db_tokens = await service.update_logout(refresh_token)

    # NOTE: Delete cookies for access token and refresh token.
    response.delete_cookie(
        key="access_token",
        httponly=True,
    )
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
    )

    response.headers["HX-Redirect"] = "/"
    response.status_code = st.HTTP_302_FOUND
    return {
        "message": "Logout Successfully",
        "logout": [
            TokenRefresh.model_validate(
                {
                    "access_token": token.access_token,
                    "refresh_token": token.refresh_token,
                }
            ).model_dump()
            for token in db_tokens
        ],
    }
