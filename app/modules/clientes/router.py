from fastapi import APIRouter

router = APIRouter()

"""Rutas de clientes."""
from fastapi import APIRouter
from app.core.crud import Sesion, Limite, Desplazamiento
from app.modules.clientes import service
from app.modules.clientes.schemas import ClienteCreate, ClienteUpdate, ClienteRead, PerfilCreate, PerfilRead
from app.modules.ventas.schemas import VentaRead
from app.modules.ventas import service as ventas_service

router = APIRouter(prefix="/clientes", tags=["Clientes"])

@router.post("/", response_model=ClienteRead, status_code=201)
async def crear(datos: ClienteCreate, session: Sesion):
    return await service.crear(session, datos)

@router.get("/{cliente_id}", response_model=ClienteRead)
async def obtener(cliente_id: int, session: Sesion):
    return await service.obtener(session, cliente_id)

@router.patch("/{cliente_id}", response_model=ClienteRead)
async def actualizar(cliente_id: int, datos: ClienteUpdate, session: Sesion):
    return await service.actualizar(session, cliente_id, datos)

@router.post("/{cliente_id}/perfil", response_model=PerfilRead, status_code=201)
async def crear_perfil(cliente_id: int, datos: PerfilCreate, session: Sesion):
    return await service.crear_perfil(session, cliente_id, datos)

@router.get("/{cliente_id}/ventas", response_model=list[VentaRead])
async def ventas(cliente_id: int, session: Sesion, limit: Limite = 20, offset: Desplazamiento = 0):
    await service.obtener(session, cliente_id)
    return await ventas_service.listar(session, limit, offset, cliente_id)
