from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from app.core.settings import settings
from app.api.routers.main import main_router

app = FastAPI(
    title=settings.title,
    description=settings.description,
    version=settings.version,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allow_origins,
    allow_credentials=settings.allow_credentials,
    allow_methods=settings.allow_methods,
    allow_headers=settings.allow_headers,
)
app.include_router(main_router)
