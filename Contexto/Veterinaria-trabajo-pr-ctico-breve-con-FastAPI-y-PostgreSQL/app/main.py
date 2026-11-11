"""Aplicación de la veterinaria y ciclo de vida de sus recursos."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

import app.core.modelos  # Registra las seis tablas sin crear el esquema ni abrir conexiones.
from app.core.config import obtener_database_url
from app.core.database import crear_fabrica_de_sesiones, crear_motor
from app.modules.duenios.router import router as duenios_router
from app.modules.health.router import router as health_router
from app.modules.laboratorio.router import router as laboratorio_router
from app.modules.mascotas.router import router as mascotas_router
from app.modules.practicas.router import router as practicas_router
from app.modules.turnos.router import router as turnos_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    motor = crear_motor(obtener_database_url())
    try:
        app.state.motor = motor
        app.state.fabrica_de_sesiones = crear_fabrica_de_sesiones(motor)
        # Las tablas se crearán con reiniciar.py, no al iniciar el servidor.
        yield
    finally:
        await motor.dispose()


app = FastAPI(title="Veterinaria", version="0.1.0", lifespan=lifespan)
app.include_router(health_router)
app.include_router(duenios_router)
app.include_router(mascotas_router)
app.include_router(practicas_router)
app.include_router(turnos_router)
app.include_router(laboratorio_router)
