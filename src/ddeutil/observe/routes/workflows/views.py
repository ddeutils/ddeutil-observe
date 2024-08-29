from fastapi import APIRouter, Depends, Request

from ...deps import get_templates

workflows = APIRouter(prefix="/workflows", tags=["workflows"])


@workflows.get("/")
def get_workflows(request: Request, templates=Depends(get_templates)):
    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            "workflows/partials/show_add_author_form.html", {"request": request}
        )
    return templates.TemplateResponse(
        request=request, name="workflows/index.html"
    )
