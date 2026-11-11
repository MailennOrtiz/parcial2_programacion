"""Aplicación de la librería y ciclo de vida de sus recursos."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import SQLModel

import app.core.modelos  # Registra las tablas antes de crear el esquema.
from app.core.config import obtener_database_url, obtener_sql_echo
from app.core.database import crear_fabrica_de_sesiones, crear_motor
from app.modules.health.router import router as health_router
from app.modules.editoriales.router import router as editoriales_router
from app.modules.generos.router import router as generos_router
from app.modules.autores.router import router as autores_router
from app.modules.libros.router import router as libros_router
from app.modules.clientes.router import router as clientes_router
from app.modules.ventas.router import router as ventas_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    motor = crear_motor(obtener_database_url(), obtener_sql_echo())
    app.state.motor = motor
    app.state.fabrica_de_sesiones = crear_fabrica_de_sesiones(motor)
    async with motor.begin() as conexion:
        await conexion.run_sync(SQLModel.metadata.create_all)
    try:
        yield
    finally:
        await motor.dispose()


app = FastAPI(title="Librería", version="0.1.0", lifespan=lifespan)
app.include_router(health_router)
app.include_router(editoriales_router)
app.include_router(generos_router)
app.include_router(autores_router)
app.include_router(libros_router)
app.include_router(clientes_router)
app.include_router(ventas_router)
