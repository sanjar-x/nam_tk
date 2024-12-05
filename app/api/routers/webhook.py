from fastapi.routing import APIRouter


# Github
from ..endpoints.webhooks.github import github_router

webhook_router = APIRouter(prefix="/webhooks")
webhook_router.include_router(github_router, tags=["GITGUB WEBHOOKS"])
