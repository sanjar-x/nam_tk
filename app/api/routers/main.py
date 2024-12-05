from fastapi.routing import APIRouter


from app.api.endpoints.main.documents import documents_router
from app.api.endpoints.main.settings import settings_router

main_router = APIRouter()
main_router.include_router(documents_router, tags=["DOCUMENTS"])
main_router.include_router(settings_router, tags=["SETTINGS"])
