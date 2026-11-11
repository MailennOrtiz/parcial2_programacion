"""Rutas HTTP de dueños y fichas: reciben datos y delegan al service."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Response, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.modules.duenios import service
from app.modules.duenios.schemas import DuenioCreate, DuenioRead, DuenioUpdate, FichaCreate, FichaRead
from app.modules.mascotas.schemas import MascotaRead


router = APIRouter(prefix="/duenios", tags=["Dueños"])
Sesion = Annotated[AsyncSession, Depends(get_session)]
Id = Annotated[int, Path(gt=0)]


@router.post("/", response_model=DuenioRead, status_code=status.HTTP_201_CREATED)
async def crear(datos: DuenioCreate, session: Sesion):
    return await service.crear_duenio(session, datos)


@router.get("/{id}", response_model=DuenioRead)
async def obtener(id: Id, session: Sesion):
    return await service.obtener_duenio(session, id)


@router.patch("/{id}", response_model=DuenioRead)
async def actualizar(id: Id, datos: DuenioUpdate, session: Sesion):
    return await service.actualizar_duenio(session, id, datos)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def borrar(id: Id, session: Sesion) -> Response:
    await service.borrar_duenio(session, id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{id}/ficha", response_model=FichaRead, status_code=status.HTTP_201_CREATED)
async def crear_ficha(id: Id, datos: FichaCreate, session: Sesion):
    return await service.crear_ficha(session, id, datos)


@router.get("/{id}/mascotas", response_model=list[MascotaRead])
async def mascotas(id: Id, session: Sesion):
    return await service.listar_mascotas(session, id)
