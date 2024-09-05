# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi import status as st
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from .__about__ import __version__
from .auth import api_auth, auth
from .conf import config
from .db import sessionmanager
from .routes import api_router, workflow
from .utils import get_logger

load_dotenv()
logger = get_logger("ddeutil.observe")
sessionmanager.init(config.OBSERVE_SQLALCHEMY_DB_ASYNC_URL)


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    if sessionmanager.is_opened():
        await sessionmanager.close()


app = FastAPI(
    titile="Observe Web",
    version=__version__,
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:8080",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

# NOTE: Authentication
app.include_router(api_auth, prefix="/api/v1")
app.include_router(auth)

# NOTE: Any routers
app.include_router(api_router, prefix="/api/v1")
app.include_router(workflow)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def home(request: Request):
    return RedirectResponse(
        request.url_for("read_workflows"), status_code=st.HTTP_303_SEE_OTHER
    )
