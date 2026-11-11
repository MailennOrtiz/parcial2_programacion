from fastapi import APIRouter

router = APIRouter()

"""Rutas de editoriales."""
from fastapi import APIRouter
from app.core.crud import Sesion, Limite, Desplazamiento
from app.modules.editoriales import service
from app.modules.editoriales.schemas import EditorialCreate, EditorialUpdate, EditorialRead
from app.modules.libros.schemas import LibroResumenRead
from app.modules.libros import service as libros_service

router = APIRouter(prefix="/editoriales", tags=["Editoriales"])

@router.post("/", response_model=EditorialRead, status_code=201)
async def crear(datos: EditorialCreate, session: Sesion):
    return await service.crear(session, datos)

@router.get("/", response_model=list[EditorialRead])
async def listar(session: Sesion, limit: Limite = 20, offset: Desplazamiento = 0):
    return await service.listar(session, limit, offset)

@router.get("/{editorial_id}", response_model=EditorialRead)
async def obtener(editorial_id: int, session: Sesion):
    return await service.obtener(session, editorial_id)

@router.patch("/{editorial_id}", response_model=EditorialRead)
async def actualizar(editorial_id: int, datos: EditorialUpdate, session: Sesion):
    return await service.actualizar(session, editorial_id, datos)

@router.get("/{editorial_id}/libros", response_model=list[LibroResumenRead])
async def libros(editorial_id: int, session: Sesion, limit: Limite = 20, offset: Desplazamiento = 0):
    await service.obtener(session, editorial_id)
    return await libros_service.listar(session, limit, offset, editorial_id=editorial_id)
