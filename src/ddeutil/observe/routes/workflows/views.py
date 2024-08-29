from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Header, Request

from ...deps import get_templates

workflows = APIRouter(prefix="/workflows", tags=["workflows"])


@workflows.get("/")
def get_workflows(
    request: Request,
    hx_request: Annotated[Optional[str], Header(...)] = None,
    templates=Depends(get_templates),
):
    """Return all workflows."""
    if hx_request:
        return templates.TemplateResponse(
            "workflows/partials/show_add_author_form.html", {"request": request}
        )
    return templates.TemplateResponse(
        request=request, name="workflows/index.html"
    )
