from fastapi import APIRouter

router = APIRouter()

"""Rutas de libros."""
from fastapi import APIRouter, Query
from app.core.crud import Sesion, Limite, Desplazamiento
from app.modules.libros import service
from app.modules.libros.schemas import LibroCreate, LibroUpdate, LibroRead, LibroResumenRead

router = APIRouter(prefix="/libros", tags=["Libros"])

@router.post("/", response_model=LibroRead, status_code=201)
async def crear(datos: LibroCreate, session: Sesion):
    return await service.crear(session, datos)

@router.get("/", response_model=list[LibroResumenRead])
async def listar(session: Sesion, limit: Limite = 20, offset: Desplazamiento = 0,
                 titulo: str | None = None, genero_id: int | None = Query(default=None, gt=0)):
    return await service.listar(session, limit, offset, titulo=titulo, genero_id=genero_id)

@router.get("/{libro_id}", response_model=LibroRead)
async def obtener(libro_id: int, session: Sesion):
    return service.lectura(await service.obtener(session, libro_id))

@router.patch("/{libro_id}", response_model=LibroRead)
async def actualizar(libro_id: int, datos: LibroUpdate, session: Sesion):
    return await service.actualizar(session, libro_id, datos)
