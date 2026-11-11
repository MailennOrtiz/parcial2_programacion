"""Altas, detalle con dueño y paginación estable de mascotas."""

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, raiseload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.errores import conflicto
from app.modules.mascotas.models import Mascota
from app.modules.mascotas.schemas import MascotaCreate, MascotaRead, MascotasPage


async def crear_mascota(session: AsyncSession, datos: MascotaCreate) -> Mascota:
    mascota = Mascota(**datos.model_dump())
    session.add(mascota)
    try:
        await session.commit()
    except IntegrityError as error:
        await session.rollback()
        raise conflicto("La mascota apunta a un dueño que no existe.") from error
    return mascota


async def obtener_mascota(session: AsyncSession, mascota_id: int) -> Mascota:
    consulta = select(Mascota).where(Mascota.id == mascota_id).options(
        joinedload(Mascota.duenio), raiseload("*")
    )
    mascota = (await session.exec(consulta)).first()
    if mascota is None:
        raise HTTPException(status_code=404, detail="Mascota no encontrada.")
    return mascota


async def listar_mascotas(session: AsyncSession, page: int, size: int) -> MascotasPage:
    total = (await session.exec(select(func.count()).select_from(Mascota))).one()
    pages = (total + size - 1) // size
    # Sin resultados, pages es 0 y la primera página es una excepción válida.
    if page > pages and page != 1:
        raise HTTPException(status_code=422, detail="La página solicitada no existe.")
    consulta = select(Mascota).order_by(Mascota.id).offset((page - 1) * size).limit(size)
    mascotas = (await session.exec(consulta)).all()
    return MascotasPage(
        items=[MascotaRead.model_validate(mascota) for mascota in mascotas],
        total=total, page=page, size=size, pages=pages,
    )
