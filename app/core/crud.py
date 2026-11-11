"""Operaciones comunes sin consultas previas de unicidad."""

from typing import Annotated

from fastapi import Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session

Sesion = Annotated[AsyncSession, Depends(get_session)]
Limite = Annotated[int, Query(ge=1, le=100)]
Desplazamiento = Annotated[int, Query(ge=0)]


async def guardar(session: AsyncSession, objeto) -> None:
    session.add(objeto)
    try:
        await session.commit()
    except IntegrityError as error:
        await session.rollback()
        raise HTTPException(status_code=409, detail="La base rechazó la operación por un conflicto de datos.") from error


async def obtener(session: AsyncSession, modelo, identificador: int):
    objeto = await session.get(modelo, identificador)
    if objeto is None:
        raise HTTPException(status_code=404, detail="Recurso no encontrado.")
    return objeto


async def listar(session: AsyncSession, modelo, limit: int, offset: int):
    return (await session.exec(select(modelo).order_by(modelo.id).limit(limit).offset(offset))).all()


async def actualizar(session: AsyncSession, modelo, identificador: int, datos):
    objeto = await obtener(session, modelo, identificador)
    objeto.sqlmodel_update(datos.model_dump(exclude_unset=True))
    await guardar(session, objeto)
    return objeto
