"""Chequeos de vida y disponibilidad, sin lógica de persistencia en el router."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.modules.health.schemas import LiveRead, ReadyRead
from app.modules.health.service import comprobar_base


router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/live", response_model=LiveRead)
async def live() -> LiveRead:
    # No depende de get_session: sigue respondiendo aunque PostgreSQL esté caído.
    return LiveRead()


@router.get("/ready", response_model=ReadyRead, responses={503: {"description": "Base no disponible"}})
async def ready(session: Annotated[AsyncSession, Depends(get_session)]) -> ReadyRead:
    await comprobar_base(session)
    return ReadyRead()
