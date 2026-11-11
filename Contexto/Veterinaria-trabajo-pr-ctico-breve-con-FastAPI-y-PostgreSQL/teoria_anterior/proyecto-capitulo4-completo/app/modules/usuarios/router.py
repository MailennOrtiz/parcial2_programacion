from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import consultas_emitidas, get_session
from app.modules.pedidos.schemas import PedidoRead
from app.modules.usuarios import service
from app.modules.usuarios.schemas import (
    PerfilCreate,
    PerfilRead,
    QueHayEnMemoria,
    UsuarioConPedidosYConsultas,
    UsuarioConPrimerPedidoCreate,
    UsuarioConPrimerPedidoRead,
    UsuarioCreate,
    UsuarioRead,
)

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


# ─── Usuario ─────────────────────────────────────────────────────────────────
@router.post("/", response_model=UsuarioRead, status_code=201)
async def crear_usuario(datos: UsuarioCreate, session: AsyncSession = Depends(get_session)):
    return await service.crear_usuario(session, datos)


# diapositiva 11. Ruta fija: va antes de /{usuario_id}.
@router.post("/con-primer-pedido", response_model=UsuarioConPrimerPedidoRead, status_code=201)
async def crear_usuario_con_primer_pedido(
    datos: UsuarioConPrimerPedidoCreate, session: AsyncSession = Depends(get_session)
):
    """Alta de un usuario con su primer pedido: back_populates en acción."""
    return await service.crear_usuario_con_primer_pedido(session, datos)


@router.get("/", response_model=list[UsuarioRead])
async def listar_usuarios(session: AsyncSession = Depends(get_session)):
    """La tabla usuario tal cual está guardada: `id` y `nombre`, nada más."""
    return await service.listar_usuarios(session)


@router.get("/{usuario_id}", response_model=UsuarioRead)
async def obtener_usuario(usuario_id: int, session: AsyncSession = Depends(get_session)):
    usuario = await service.obtener_usuario(session, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


# ─── Uno a muchos (diapositiva 4) ───────────────────────────────────
@router.get("/{usuario_id}/pedidos", response_model=list[PedidoRead])
async def pedidos_del_usuario(usuario_id: int, session: AsyncSession = Depends(get_session)):
    """Los pedidos de un usuario: `SELECT ... FROM pedido WHERE usuario_id = …`."""
    return await service.pedidos_del_usuario(session, usuario_id)


# ─── Uno a uno (diapositiva 5) ──────────────────────────────────────
@router.post("/{usuario_id}/perfil", response_model=PerfilRead, status_code=201)
async def crear_perfil(
    usuario_id: int, datos: PerfilCreate, session: AsyncSession = Depends(get_session)
):
    """Tabla `perfil`, con unicidad: un segundo perfil devuelve 409."""
    return await service.crear_perfil(session, usuario_id, datos)


@router.get("/{usuario_id}/perfil", response_model=list[PerfilRead])
async def perfiles_del_usuario(usuario_id: int, session: AsyncSession = Depends(get_session)):
    """Devuelve una lista a propósito: con unicidad, nunca trae más de uno."""
    return await service.perfiles_del_usuario(session, usuario_id)


@router.post("/{usuario_id}/perfil-sin-unicidad", response_model=PerfilRead, status_code=201)
async def crear_perfil_sin_unicidad(
    usuario_id: int, datos: PerfilCreate, session: AsyncSession = Depends(get_session)
):
    """Tabla `perfil_sin_unicidad` (contraejemplo): acepta todos los que le manden."""
    return await service.crear_perfil_sin_unicidad(session, usuario_id, datos)


@router.get("/{usuario_id}/perfil-sin-unicidad", response_model=list[PerfilRead])
async def perfiles_sin_unicidad(usuario_id: int, session: AsyncSession = Depends(get_session)):
    return await service.perfiles_sin_unicidad_del_usuario(session, usuario_id)


# ═══════════════════════════════════════════════════════════════════════════
# PARTE 2 · CÓMO SE LEEN
# ═══════════════════════════════════════════════════════════════════════════
@router.get("/{usuario_id}/que-hay-en-memoria", response_model=QueHayEnMemoria)
async def que_hay_en_memoria(usuario_id: int, session: AsyncSession = Depends(get_session)):
    """diapositiva 12: la relación está declarada, pero no hay nada cargado."""
    datos = await service.que_hay_en_memoria(session, usuario_id)
    if not datos:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"consultas_emitidas": consultas_emitidas(session), **datos}


@router.get("/{usuario_id}/pedidos-sin-precarga", response_model=list[PedidoRead])
async def pedidos_sin_precarga(usuario_id: int, session: AsyncSession = Depends(get_session)):
    """VERSIÓN INCORRECTA a propósito (diapositiva 15): explota MissingGreenlet."""
    pedidos = await service.pedidos_sin_precarga(session, usuario_id)
    if pedidos is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return pedidos


@router.get("/{usuario_id}/con-pedidos", response_model=UsuarioConPedidosYConsultas)
async def obtener_con_pedidos(usuario_id: int, session: AsyncSession = Depends(get_session)):
    """diapositiva 14: el usuario con sus pedidos precargados (selectinload)."""
    usuario = await service.obtener_con_pedidos(session, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"consultas_emitidas": consultas_emitidas(session), "usuario": usuario}
