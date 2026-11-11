from fastapi import APIRouter

router = APIRouter()

"""Rutas de géneros."""
from fastapi import APIRouter
from app.core.crud import Sesion, Limite, Desplazamiento, obtener
from app.modules.generos import service
from app.modules.generos.models import Genero
from app.modules.generos.schemas import GeneroCreate, GeneroRead
from app.modules.libros.schemas import LibroResumenRead
from app.modules.libros import service as libros_service

router = APIRouter(prefix="/generos", tags=["Géneros"])

@router.post("/", response_model=GeneroRead, status_code=201)
async def crear(datos: GeneroCreate, session: Sesion):
    return await service.crear(session, datos)

@router.get("/", response_model=list[GeneroRead])
async def listar(session: Sesion, limit: Limite = 20, offset: Desplazamiento = 0):
    return await service.listar(session, limit, offset)

@router.get("/{genero_id}/libros", response_model=list[LibroResumenRead])
async def libros(genero_id: int, session: Sesion, limit: Limite = 20, offset: Desplazamiento = 0):
    await obtener(session, Genero, genero_id)
    return await libros_service.listar(session, limit, offset, genero_id=genero_id)
