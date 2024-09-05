from fastapi import APIRouter

from .workflow.routes import workflow as workflow_api
from .workflow.views import workflow

api_router = APIRouter()
api_router.include_router(workflow_api)


@api_router.get("/")
async def health():
    return {"message": "Standby ..."}
