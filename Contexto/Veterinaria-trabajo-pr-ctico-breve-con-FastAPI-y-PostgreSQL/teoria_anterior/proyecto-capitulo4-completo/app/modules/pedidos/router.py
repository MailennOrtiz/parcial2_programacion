from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import consultas_emitidas, get_session
from app.modules.pedidos import service
from app.modules.pedidos.schemas import (
    DetalleCreate,
    DetalleRead,
    FilasDelJoinYConsultas,
    PedidoCompletoYConsultas,
    PedidoConDetallesRead,
    PedidoConUsuario,
    PedidoCreate,
    PedidoRead,
    PedidosConLineasYConsultas,
)

router = APIRouter(prefix="/pedidos", tags=["pedidos"])

# Orden de las rutas: las fijas (/detalles, /n-mas-1, ...) van ANTES de
# /{pedido_id}. FastAPI prueba las rutas en orden, y si /{pedido_id} viniera
# primero, "/pedidos/n-mas-1" intentaría convertir "n-mas-1" en un número.


# ─── Clave foránea (diapositiva 4) · asociación y composición ───────
@router.post("/", response_model=PedidoConDetallesRead, status_code=201)
async def crear_pedido(datos: PedidoCreate, session: AsyncSession = Depends(get_session)):
    """Crea el pedido con sus líneas: viaja el id del usuario y los datos de las líneas.

    Si `usuario_id` o algún `producto_id` no existe, la base responde con un
    409 y no se guarda nada. La vuelta trae el pedido con su usuario y sus líneas.
    """
    return await service.crear_pedido(session, datos)


@router.get("/", response_model=list[PedidoRead])
async def listar_pedidos(session: AsyncSession = Depends(get_session)):
    """La tabla pedido tal cual está guardada."""
    return await service.listar_pedidos(session)


@router.get("/con-usuario", response_model=list[PedidoConUsuario])
async def listar_pedidos_con_usuario(session: AsyncSession = Depends(get_session)):
    """Los pedidos con el nombre de su dueño (JOIN con usuario)."""
    return await service.listar_pedidos_con_usuario(session)


# ─── Composición (diapositiva 7) ───────────────────────────────
@router.get("/detalles", response_model=list[DetalleRead])
async def listar_todos_los_detalles(session: AsyncSession = Depends(get_session)):
    """Las líneas de todos los pedidos."""
    return await service.listar_detalles(session)


# ═══ Parte 2 · rutas fijas ═════════════════════════════════════════════════
@router.get("/n-mas-1", response_model=PedidosConLineasYConsultas)
async def listar_con_detalles_n_mas_1(session: AsyncSession = Depends(get_session)):
    """VERSIÓN INCORRECTA a propósito (diapositiva 13): 1 consulta + 1 por pedido."""
    pedidos = await service.listar_con_detalles_n_mas_1(session)
    return {"consultas_emitidas": consultas_emitidas(session), "pedidos": pedidos}


@router.get("/con-detalles-selectinload", response_model=PedidosConLineasYConsultas)
async def listar_con_detalles_selectinload(session: AsyncSession = Depends(get_session)):
    """Los pedidos con sus líneas, precargadas con selectinload: 2 consultas."""
    pedidos = await service.listar_con_detalles_selectinload(session)
    return {"consultas_emitidas": consultas_emitidas(session), "pedidos": pedidos}


@router.get("/con-detalles-joinedload", response_model=PedidosConLineasYConsultas)
async def listar_con_detalles_joinedload(session: AsyncSession = Depends(get_session)):
    """Los mismos datos con joinedload: 1 consulta con JOIN (diapositiva 14)."""
    pedidos = await service.listar_con_detalles_joinedload(session)
    return {"consultas_emitidas": consultas_emitidas(session), "pedidos": pedidos}


@router.get("/filas-del-join", response_model=FilasDelJoinYConsultas)
async def filas_del_join(session: AsyncSession = Depends(get_session)):
    """Las filas crudas del JOIN: los datos del pedido, repetidos por línea."""
    filas = await service.filas_del_join(session)
    return {"consultas_emitidas": consultas_emitidas(session), "filas": filas}


# ─── Pedido puntual (Parte 1) ────────────────────────────────────────────────
@router.get("/{pedido_id}", response_model=PedidoRead)
async def obtener_pedido(pedido_id: int, session: AsyncSession = Depends(get_session)):
    pedido = await service.obtener_pedido(session, pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return pedido


@router.delete("/{pedido_id}", status_code=204)
async def borrar_pedido(pedido_id: int, session: AsyncSession = Depends(get_session)):
    """Borra el pedido. Sus líneas se van con él: cascada."""
    if not await service.borrar_pedido(session, pedido_id):
        raise HTTPException(status_code=404, detail="Pedido no encontrado")


@router.get("/{pedido_id}/detalles", response_model=list[DetalleRead])
async def listar_detalles(pedido_id: int, session: AsyncSession = Depends(get_session)):
    return await service.listar_detalles(session, pedido_id=pedido_id)


@router.post("/{pedido_id}/detalles", response_model=DetalleRead, status_code=201)
async def agregar_detalle(
    pedido_id: int, datos: DetalleCreate, session: AsyncSession = Depends(get_session)
):
    return await service.agregar_detalle(session, pedido_id, datos)


# ═══ Parte 2 · un pedido puntual ═══════════════════════════════════════════
@router.get("/{pedido_id}/sin-precarga", response_model=list[DetalleRead])
async def obtener_sin_precarga(pedido_id: int, session: AsyncSession = Depends(get_session)):
    """VERSIÓN INCORRECTA a propósito (diapositiva 15): explota MissingGreenlet."""
    return await service.obtener_sin_precarga(session, pedido_id)


@router.get("/{pedido_id}/con-detalles", response_model=PedidoCompletoYConsultas)
async def obtener_con_detalles(pedido_id: int, session: AsyncSession = Depends(get_session)):
    """El pedido con su usuario y sus líneas, precargados (diapositiva 14): 3 consultas."""
    pedido = await service.obtener_con_detalles(session, pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return {"consultas_emitidas": consultas_emitidas(session), "pedido": pedido}
