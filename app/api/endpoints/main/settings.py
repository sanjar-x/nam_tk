import random
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.core.database import engine
from app.core.models import Base

settings_router = APIRouter()


@settings_router.get("/database/init")
async def init_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        return JSONResponse(content={"database": "initialized"})


@settings_router.get("/database/drop")
async def drop_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        return JSONResponse(content={"database": "droped"})


@settings_router.get("/database/reload")
async def reload_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        return JSONResponse(content={"database": "reloaded"})
