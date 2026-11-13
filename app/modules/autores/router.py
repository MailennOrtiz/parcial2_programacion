from fastapi import APIRouter

router = APIRouter()

"""Rutas de autores."""
from fastapi import APIRouter
from app.core.crud import Sesion, Limite, Desplazamiento
from app.modules.autores import service
from app.modules.autores.schemas import AutorCreate, AutorUpdate, AutorRead
from app.modules.libros.schemas import LibroDeAutorRead

router = APIRouter(prefix="/autores", tags=["Autores"])

@router.post("/", response_model=AutorRead, status_code=201)
async def crear(datos: AutorCreate, session: Sesion):
    return await service.crear(session, datos)

@router.get("/", response_model=list[AutorRead])
async def listar(session: Sesion, limit: Limite = 20, offset: Desplazamiento = 0):
    return await service.listar(session, limit, offset)

@router.get("/{autor_id}", response_model=AutorRead)
async def obtener(autor_id: int, session: Sesion):
    return await service.obtener(session, autor_id)

@router.patch("/{autor_id}", response_model=AutorRead)
async def actualizar(autor_id: int, datos: AutorUpdate, session: Sesion):
    return await service.actualizar(session, autor_id, datos)

@router.get("/{autor_id}/libros", response_model=list[LibroDeAutorRead])
async def libros(autor_id: int, session: Sesion, limit: Limite = 20, offset: Desplazamiento = 0):
    return await service.libros(session, autor_id, limit, offset)
