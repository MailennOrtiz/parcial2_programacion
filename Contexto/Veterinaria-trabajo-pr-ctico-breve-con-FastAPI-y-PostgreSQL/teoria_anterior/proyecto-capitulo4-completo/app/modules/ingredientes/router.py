from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.modules.ingredientes import service
from app.modules.ingredientes.schemas import (
    IngredienteCreate,
    IngredienteRead,
    ProductoQueLoLleva,
)

router = APIRouter(prefix="/ingredientes", tags=["ingredientes"])


@router.post("/", response_model=IngredienteRead, status_code=201)
async def crear_ingrediente(
    datos: IngredienteCreate, session: AsyncSession = Depends(get_session)
):
    return await service.crear_ingrediente(session, datos)


@router.get("/", response_model=list[IngredienteRead])
async def listar_ingredientes(session: AsyncSession = Depends(get_session)):
    return await service.listar_ingredientes(session)


# ─── Muchos a muchos, desde el otro lado (diapositiva 6) ───────────────────
@router.get("/{ingrediente_id}/productos", response_model=list[ProductoQueLoLleva])
async def productos_que_lo_llevan(
    ingrediente_id: int, session: AsyncSession = Depends(get_session)
):
    """En qué productos va este ingrediente, y cuánto lleva cada uno."""
    return await service.productos_que_lo_llevan(session, ingrediente_id)
