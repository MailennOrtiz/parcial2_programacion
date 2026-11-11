# L�gica del m�dulo generos (se implementa en ejercicios posteriores).
"""Operaciones de géneros."""
from app.core import crud
from app.modules.generos.models import Genero

async def crear(session, datos):
    objeto = Genero.model_validate(datos)
    await crud.guardar(session, objeto)
    return objeto

async def listar(session, limit, offset):
    return await crud.listar(session, Genero, limit, offset)
