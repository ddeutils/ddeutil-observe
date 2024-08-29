import uvicorn
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .deps import get_templates
from .routes import workflows

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    # Update with specific origins in production
    allow_origins=["127.0.0.1"],
    allow_methods=["GET", "POST"],
)
app.include_router(
    workflows,
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    templates: Jinja2Templates = Depends(get_templates),
):
    return templates.TemplateResponse(
        request=request, name="home/index.html", context={}
    )


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)
