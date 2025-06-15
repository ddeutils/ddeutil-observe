# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi import status as st
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import OperationalError

from .__about__ import __version__
from .auth import api_auth, auth
from .backend import OAuth2Backend, OAuth2Middleware
from .conf import config
from .db import sessionmanager
from .routes import (
    api_router,
    audit,
    notification,
    profile,
    trace,
    workflow,
)

logger = logging.getLogger("uvicorn.error")
PARENT_PATH: Path = Path(__file__).parent

# NOTE: Initial sqlalchemy session maker object that create instance of current
#   database pointer from `OBSERVE_SQLALCHEMY_DB_ASYNC_URL` env var.
sessionmanager.init(config.sqlalchemy_db_async_url)


@asynccontextmanager
async def lifespan(inside: FastAPI):
    """Lifespan context function that make sure the session maker instance
    already close after respond the incoming request to the client.
    """
    async with sessionmanager.connect() as conn:
        await sessionmanager.create_all(conn)

    # IMPORTANT: Initial setop data context on the backend database.
    from .initial import create_admin, create_role_policy, create_workflows

    async with sessionmanager.session() as session:
        await create_admin(session)
        await create_role_policy(session, routes=inside.routes)
        await create_workflows(session)

    yield

    if sessionmanager.is_opened():
        await sessionmanager.close()


app = FastAPI(
    titile="Observe",
    description=(
        "This is observe FastAPI application that use to display workflow "
        "and execution logging pages."
    ),
    version=__version__,
    lifespan=lifespan,
    docs_url="/api/docs",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:88",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

# NOTE: Add oauth2 backend middleware.
app.add_middleware(OAuth2Middleware, backend=OAuth2Backend())


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Custom process time middleware."""
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions, especially authentication errors."""
    # Handle authentication errors by redirecting to login
    if exc.status_code == st.HTTP_401_UNAUTHORIZED:
        if (
            exc.detail == "Could not validate credentials"
            or exc.detail == "Not authenticated"
            or exc.detail == "Token was expired"
        ):
            return RedirectResponse(
                url="/auth/login",
                status_code=st.HTTP_307_TEMPORARY_REDIRECT,
            )

    # Handle 307 redirects from authentication dependencies
    if exc.status_code == st.HTTP_307_TEMPORARY_REDIRECT:
        location = exc.headers.get("Location")
        if location:
            return RedirectResponse(
                url=location,
                status_code=st.HTTP_307_TEMPORARY_REDIRECT,
            )

    # For other HTTP exceptions, return the default response
    return PlainTextResponse(
        str(exc.detail),
        status_code=exc.status_code,
    )


@app.exception_handler(OperationalError)
async def sqlalchemy_exception_handler(_: Request, exc) -> PlainTextResponse:
    """Exception handler for SQLAlchemy package that get the error from the
    backend database.
    """
    return PlainTextResponse(
        str(exc.detail),
        status_code=st.HTTP_500_INTERNAL_SERVER_ERROR,
    )


# NOTE: Authentication
app.include_router(api_auth, prefix=config.api_prefix)
app.include_router(auth)

# NOTE: Any routers
app.include_router(api_router, prefix=config.api_prefix)
app.include_router(workflow)
app.include_router(notification)
app.include_router(profile)
app.include_router(trace)
app.include_router(audit)


# NOTE: Add Chrome DevTools endpoint - only enabled in development
@app.get("/.well-known/appspecific/com.chrome.devtools.json")
async def chrome_devtools(request: Request):
    """Handle Chrome DevTools request.
    In production, this endpoint returns 404 to avoid exposing unnecessary information.
    """
    if config.environment == "development":
        return {"protocol-version": "1.1", "security": {"enabled": True}}
    # In production/staging, return 404
    raise HTTPException(status_code=st.HTTP_404_NOT_FOUND, detail="Not Found")


# NOTE: Start mount all static files from /static path to this application.
app.mount(
    "/static",
    StaticFiles(directory=PARENT_PATH / "static"),
    name="static",
)


@app.get("/")
async def home(request: Request):
    """The home page that redirect to main page."""
    # Check if user is authenticated by looking for tokens
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")

    if not access_token and not refresh_token:
        # User is not authenticated, redirect to login
        return RedirectResponse(
            url="/auth/login",
            status_code=st.HTTP_307_TEMPORARY_REDIRECT,
        )

    # User appears to be authenticated, redirect to workflow page
    return RedirectResponse(
        url="/workflow/",
        status_code=st.HTTP_307_TEMPORARY_REDIRECT,
    )
