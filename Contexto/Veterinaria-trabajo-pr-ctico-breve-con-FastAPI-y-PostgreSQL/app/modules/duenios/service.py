"""Lógica de dueños: las restricciones las garantiza la base, no un SELECT previo."""

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, raiseload, selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.errores import conflicto
from app.modules.duenios.models import Duenio, FichaDuenio
from app.modules.duenios.schemas import DuenioCreate, DuenioUpdate, FichaCreate
from app.modules.mascotas.models import Mascota


async def obtener_duenio(session: AsyncSession, duenio_id: int) -> Duenio:
    consulta = select(Duenio).where(Duenio.id == duenio_id).options(
        joinedload(Duenio.ficha), raiseload("*")
    )
    duenio = (await session.exec(consulta)).first()
    if duenio is None:
        raise HTTPException(status_code=404, detail="Dueño no encontrado.")
    return duenio


async def crear_duenio(session: AsyncSession, datos: DuenioCreate) -> Duenio:
    duenio = Duenio(**datos.model_dump())
    session.add(duenio)
    try:
        await session.commit()
    except IntegrityError as error:
        await session.rollback()
        raise conflicto("Ya existe un dueño con ese email.") from error
    return await obtener_duenio(session, duenio.id)


async def actualizar_duenio(session: AsyncSession, duenio_id: int, datos: DuenioUpdate) -> Duenio:
    duenio = await obtener_duenio(session, duenio_id)
    duenio.sqlmodel_update(datos.model_dump(exclude_unset=True))
    try:
        await session.commit()
    except IntegrityError as error:
        await session.rollback()
        raise conflicto("Ya existe un dueño con ese email.") from error
    return await obtener_duenio(session, duenio_id)


async def borrar_duenio(session: AsyncSession, duenio_id: int) -> None:
    duenio = await obtener_duenio(session, duenio_id)
    try:
        await session.delete(duenio)
        await session.commit()
    except IntegrityError as error:
        await session.rollback()
        raise conflicto("No se puede borrar un dueño que tiene mascotas a su nombre.") from error


async def crear_ficha(session: AsyncSession, duenio_id: int, datos: FichaCreate) -> FichaDuenio:
    # Esta lectura solo resuelve el 404 del recurso de la ruta; no comprueba RN-03.
    if await session.get(Duenio, duenio_id) is None:
        raise HTTPException(status_code=404, detail="Dueño no encontrado.")
    ficha = FichaDuenio(duenio_id=duenio_id, **datos.model_dump())
    session.add(ficha)
    try:
        await session.commit()
    except IntegrityError as error:
        await session.rollback()
        raise conflicto("El dueño ya tiene una ficha o dejó de existir durante el alta.") from error
    return ficha


async def listar_mascotas(session: AsyncSession, duenio_id: int) -> list[Mascota]:
    consulta = select(Duenio).where(Duenio.id == duenio_id).options(
        selectinload(Duenio.mascotas), raiseload("*")
    )
    duenio = (await session.exec(consulta)).first()
    if duenio is None:
        raise HTTPException(status_code=404, detail="Dueño no encontrado.")
    return sorted(duenio.mascotas, key=lambda mascota: mascota.id)
