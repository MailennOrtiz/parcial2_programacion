"""Carga inicial no destructiva, con una base aislada en memoria."""
import unittest

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.datos_iniciales import cargar
from app.modules.libros.models import Libro
from app.modules.clientes.models import Cliente


class DatosInicialesTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.motor = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with self.motor.begin() as conexion:
            await conexion.run_sync(SQLModel.metadata.create_all)
        self.fabrica = async_sessionmaker(self.motor, class_=AsyncSession, expire_on_commit=False)

    async def asyncTearDown(self):
        await self.motor.dispose()

    async def test_carga_y_rechazo_sin_borrar(self):
        async with self.fabrica() as session:
            async with session.begin():
                await cargar(session)
        async with self.fabrica() as session:
            self.assertEqual(len((await session.exec(select(Libro))).all()), 2)
            self.assertEqual(len((await session.exec(select(Cliente))).all()), 1)
            with self.assertRaises(ValueError):
                await cargar(session)
        async with self.fabrica() as session:
            self.assertEqual(len((await session.exec(select(Libro))).all()), 2)
