"""Entorno compartido de pruebas HTTP: base aislada por caso, sin leer el .env."""

from contextlib import asynccontextmanager
import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel

from app.core.database import crear_fabrica_de_sesiones
from app.modules.duenios.router import router as duenios_router
from app.modules.mascotas.router import router as mascotas_router
from app.modules.practicas.router import router as practicas_router
from app.modules.turnos.router import router as turnos_router
from reiniciar import cargar_datos


class ApiTestsBase(unittest.TestCase):
    def setUp(self):
        self.sentencias = []

        @asynccontextmanager
        async def lifespan(app):
            motor = create_async_engine("sqlite+aiosqlite://")

            @event.listens_for(motor.sync_engine, "connect")
            def activar_fk(conexion, registro):
                cursor = conexion.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()

            @event.listens_for(motor.sync_engine, "before_cursor_execute")
            def registrar(conexion, cursor, sentencia, parametros, contexto, varios):
                self.sentencias.append(sentencia)

            try:
                async with motor.begin() as conexion:
                    await conexion.run_sync(SQLModel.metadata.create_all)
                fabrica = crear_fabrica_de_sesiones(motor)
                app.state.fabrica_de_sesiones = fabrica
                async with fabrica() as session:
                    async with session.begin():
                        await cargar_datos(session)
                yield
            finally:
                await motor.dispose()

        self.app = FastAPI(lifespan=lifespan)
        for router in (duenios_router, mascotas_router, practicas_router, turnos_router):
            self.app.include_router(router)
        self.client = TestClient(self.app)
        self.client.__enter__()
        self.addCleanup(self.client.__exit__, None, None, None)
        self.sentencias.clear()
