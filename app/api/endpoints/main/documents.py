from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Union
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status

from ...dependencies.session import get_session

from ....schemas.document import DocumentCreate, DocumentUpdate
from ....core.models import Document

documents_router = APIRouter(prefix="/documents")


@documents_router.post("/")
async def create_document(
    document_data: DocumentCreate,
    session: AsyncSession = Depends(get_session),
):
    new_document = Document(**document_data.model_dump())
    if not await new_document.exist_pini(session):
        new_document = await new_document.save(session)
        return new_document
    else:
        return await new_document.get_by_pini(session)


@documents_router.get("/")
async def get_documents(
    id: UUID | None = None,
    query: str | None = None,
    session: AsyncSession = Depends(get_session),
):
    document = Document()
    if id:
        document.id = id
        saved_document = await document.get(session)
        return saved_document
    elif query:
        saved_document = await document.search_by_query(session, query)
        return saved_document
    else:
        all_saved_documents = await document.get_all(session)
        return all_saved_documents


@documents_router.patch("/")
async def update_document(
    id: UUID,
    document_data: DocumentUpdate,
    session: AsyncSession = Depends(get_session),
):
    document = Document(id=id)
    updated_document = await document._update(
        session,
        **document_data.model_dump(
            exclude_none=True, exclude_unset=True, exclude_defaults=True
        ),
        examination_date=datetime.now(),
        valid_date=datetime.now() + timedelta(days=365),
    )

    return updated_document


@documents_router.delete("/")
async def delete_document(
    id: UUID,
    session: AsyncSession = Depends(get_session),
):
    document = Document(id=id)
    await document.get(session)

    await document._delete(session)
    return {"detail": "document deleted"}
