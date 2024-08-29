import pathlib

import jinja2
from fastapi import Request
from fastapi.templating import Jinja2Templates


def get_templates(request: Request) -> Jinja2Templates:
    """Dynamic multi-templating folders that support templates inside APIRouter."""
    choices = [jinja2.FileSystemLoader("./templates")]
    if request.url.path != "/":
        route: str = request.url.path.strip("/").split("/")[0]
        route_path: pathlib.Path = (
            pathlib.Path(__file__).parent / f"routes/{route}/templates"
        )
        if route_path.exists():
            choices.insert(0, jinja2.FileSystemLoader(route_path))

    return Jinja2Templates(
        directory="templates",
        loader=jinja2.ChoiceLoader(choices),
    )
