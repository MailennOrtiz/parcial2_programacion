"""Rutas de mascotas con parámetros tipados y límites de paginación."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.modules.mascotas import service
from app.modules.mascotas.schemas import MascotaCreate, MascotaDetalleRead, MascotaRead, MascotasPage


router = APIRouter(prefix="/mascotas", tags=["Mascotas"])
Sesion = Annotated[AsyncSession, Depends(get_session)]


@router.post("/", response_model=MascotaRead, status_code=status.HTTP_201_CREATED)
async def crear(datos: MascotaCreate, session: Sesion):
    return await service.crear_mascota(session, datos)


@router.get("/", response_model=MascotasPage)
async def listar(
    session: Sesion,
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 20,
):
    return await service.listar_mascotas(session, page, size)


@router.get("/{id}", response_model=MascotaDetalleRead)
async def obtener(id: Annotated[int, Path(gt=0)], session: Sesion):
    return await service.obtener_mascota(session, id)
