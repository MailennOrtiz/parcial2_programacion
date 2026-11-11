from fastapi import APIRouter

router = APIRouter()

"""Rutas de ventas; no se admiten modificaciones posteriores."""
from fastapi import APIRouter
from app.core.crud import Sesion, Limite, Desplazamiento
from app.modules.ventas import service
from app.modules.ventas.schemas import VentaCreate, VentaRead

router = APIRouter(prefix="/ventas", tags=["Ventas"])

@router.post("/", response_model=VentaRead, status_code=201)
async def crear(datos: VentaCreate, session: Sesion):
    return await service.crear(session, datos)

@router.get("/", response_model=list[VentaRead])
async def listar(session: Sesion, limit: Limite = 20, offset: Desplazamiento = 0):
    return await service.listar(session, limit, offset)

@router.get("/{venta_id}", response_model=VentaRead)
async def obtener(venta_id: int, session: Sesion):
    return await service.obtener(session, venta_id)
