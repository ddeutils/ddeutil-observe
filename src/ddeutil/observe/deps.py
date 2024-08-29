import pathlib

from fastapi import Request
from fastapi.templating import Jinja2Templates
from jinja2 import ChoiceLoader, FileSystemLoader

from .db import SessionLocal


def get_templates(request: Request) -> Jinja2Templates:
    """Dynamic multi-templating Jinja2 loader that support templates inside
    APIRouter.
    """
    choices: list[FileSystemLoader] = [FileSystemLoader("./templates")]
    if request.url.path != "/":
        route: str = request.url.path.strip("/").split("/")[0]
        route_path: pathlib.Path = (
            pathlib.Path(__file__).parent / f"routes/{route}/templates"
        )
        if route_path.exists():
            choices.insert(0, FileSystemLoader(route_path))

    return Jinja2Templates(
        directory="templates",
        loader=ChoiceLoader(choices),
    )


def get_db() -> SessionLocal:
    """Return the database local session instance."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
