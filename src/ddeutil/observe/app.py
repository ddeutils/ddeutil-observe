# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
from __future__ import annotations

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .__about__ import __version__
from .deps import get_db, get_templates
from .routes import log, workflow
from .utils import get_logger

load_dotenv()
logger = get_logger("ddeutil.observe")

app = FastAPI(
    titile="Observe Web",
    version=__version__,
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
app.include_router(workflow)
app.include_router(log)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    templates: Jinja2Templates = Depends(get_templates),
    db: Session = Depends(get_db),
):
    return templates.TemplateResponse(
        request=request, name="home/index.html", context={}
    )
