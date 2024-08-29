import logging

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .deps import get_db, get_templates
from .routes import workflows

logger = logging.getLogger("ddeutil.observe")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    # TODO: Update with specific origins in production
    allow_origins=["127.0.0.1"],
    allow_methods=["GET", "POST"],
)
app.include_router(workflows)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    templates: Jinja2Templates = Depends(get_templates),
    db: Session = Depends(get_db),
):
    logger.info(str(db))
    return templates.TemplateResponse(
        request=request, name="home/index.html", context={}
    )
