# L�gica del m�dulo editoriales (se implementa en ejercicios posteriores).
"""Operaciones de editoriales."""
from app.core import crud
from app.modules.editoriales.models import Editorial

async def crear(session, datos):
    objeto = Editorial.model_validate(datos)
    await crud.guardar(session, objeto)
    return objeto

async def listar(session, limit, offset):
    return await crud.listar(session, Editorial, limit, offset)

async def obtener(session, identificador):
    return await crud.obtener(session, Editorial, identificador)

async def actualizar(session, identificador, datos):
    return await crud.actualizar(session, Editorial, identificador, datos)
