"""Motor por aplicación y sesión independiente por petición."""

from collections.abc import AsyncIterator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession


def crear_motor(database_url: str, echo: bool = False) -> AsyncEngine:
    """Construye el pool sin abrir una conexión ni crear tablas."""
    return create_async_engine(database_url, echo=echo)


def crear_fabrica_de_sesiones(motor: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(motor, class_=AsyncSession, expire_on_commit=False)


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    fabrica: async_sessionmaker[AsyncSession] = request.app.state.fabrica_de_sesiones
    async with fabrica() as session:
        yield session