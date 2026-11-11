"""Catálogo: unicidad y precios positivos garantizados por PostgreSQL."""

from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.errores import conflicto
from app.modules.practicas.models import Practica
from app.modules.practicas.schemas import PracticaCreate


async def crear_practica(session: AsyncSession, datos: PracticaCreate) -> Practica:
    practica = Practica(**datos.model_dump())
    session.add(practica)
    try:
        await session.commit()
    except IntegrityError as error:
        await session.rollback()
        raise conflicto("No se pudo guardar la práctica: nombre repetido o precio inválido.") from error
    return practica


async def listar_practicas(session: AsyncSession) -> list[Practica]:
    return list((await session.exec(select(Practica).order_by(Practica.id))).all())
