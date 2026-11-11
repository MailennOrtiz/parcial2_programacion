"""Alta, detalle y borrado de turnos."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Response, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.modules.turnos import service
from app.modules.turnos.schemas import TurnoCreate, TurnoRead


router = APIRouter(prefix="/turnos", tags=["Turnos"])
Sesion = Annotated[AsyncSession, Depends(get_session)]
Id = Annotated[int, Path(gt=0)]


@router.post("/", response_model=TurnoRead, status_code=status.HTTP_201_CREATED)
async def crear(datos: TurnoCreate, session: Sesion):
    return await service.crear_turno(session, datos)


@router.get("/{id}", response_model=TurnoRead)
async def obtener(id: Id, session: Sesion):
    return await service.detalle_turno(session, id)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def borrar(id: Id, session: Sesion) -> Response:
    await service.borrar_turno(session, id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
