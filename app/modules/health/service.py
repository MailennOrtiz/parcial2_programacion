"""Comprobación asincrónica y acotada de disponibilidad de PostgreSQL."""

import asyncio

from asyncpg import PostgresError
from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel.ext.asyncio.session import AsyncSession


TIEMPO_MAXIMO_READY = 3


async def comprobar_base(session: AsyncSession) -> None:
    try:
        async with asyncio.timeout(TIEMPO_MAXIMO_READY):
            await session.execute(text("SELECT 1"))
    except (SQLAlchemyError, PostgresError, OSError, TimeoutError) as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="La base de datos no está disponible.",
        ) from error