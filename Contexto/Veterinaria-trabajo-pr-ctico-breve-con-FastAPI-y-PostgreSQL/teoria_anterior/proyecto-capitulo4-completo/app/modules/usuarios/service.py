from fastapi import HTTPException
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError, MissingGreenlet
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.errores import CLAVE_FORANEA, codigo_de, rechazo
from app.modules.pedidos.models import Pedido
from app.modules.usuarios.models import Perfil, PerfilSinUnicidad, Usuario
from app.modules.usuarios.schemas import (
    PerfilCreate,
    UsuarioConPrimerPedidoCreate,
    UsuarioCreate,
)


# ─── Usuario ─────────────────────────────────────────────────────────────────
async def crear_usuario(session: AsyncSession, datos: UsuarioCreate) -> Usuario:
    # El id lo asigna la base; no hay nada que pueda rechazar el alta.
    usuario = Usuario.model_validate(datos)
    session.add(usuario)
    await session.commit()
    return usuario


async def listar_usuarios(session: AsyncSession) -> list[Usuario]:
    return list((await session.exec(select(Usuario).order_by(Usuario.id))).all())


async def obtener_usuario(session: AsyncSession, usuario_id: int) -> Usuario | None:
    return await session.get(Usuario, usuario_id)


# ─── Uno a muchos (diapositiva 4) ───────────────────────────────────
async def pedidos_del_usuario(session: AsyncSession, usuario_id: int) -> list[Pedido]:
    """"Los pedidos de Marta" no se leen de la fila de Marta: se BUSCAN.

    SELECT ... FROM pedido WHERE usuario_id = :usuario_id

    La tabla usuario no participa de la consulta. Los pedidos se encuentran
    porque cada uno lleva anotado de quién es.
    """
    consulta = select(Pedido).where(Pedido.usuario_id == usuario_id).order_by(Pedido.id)
    return list((await session.exec(consulta)).all())


# ─── Uno a uno (diapositiva 5) ──────────────────────────────────────
async def crear_perfil(session: AsyncSession, usuario_id: int, datos: PerfilCreate) -> Perfil:
    """Con `unique=True`: el segundo perfil del mismo usuario lo rechaza la base.

    Fijate que acá no hay ningún `if` que pregunte "¿ya tiene perfil?". Se
    intenta escribir y es la restricción de unicidad la que decide.
    """
    perfil = Perfil(usuario_id=usuario_id, apodo=datos.apodo)
    session.add(perfil)
    try:
        await session.commit()
    except IntegrityError as error:
        await session.rollback()
        # codigo_de() lee el SQLSTATE: 23503 es "clave foránea"; 23505, "unicidad".
        if codigo_de(error) == CLAVE_FORANEA:
            mensaje = "El perfil apunta a un usuario que no existe."
        else:
            mensaje = "Ese usuario ya tiene un perfil: es uno a uno."
        raise rechazo(mensaje, error) from error
    return perfil


async def perfiles_del_usuario(session: AsyncSession, usuario_id: int) -> list[Perfil]:
    """El perfil del usuario, navegando `usuario.perfil` (precargado).

    `usuario.perfil` es UN perfil o None (uselist=False): la base garantiza
    que no puede haber dos. Se devuelve en una lista para comparar con la
    tabla sin unicidad, que sí puede devolver varios.
    """
    consulta = (
        select(Usuario).where(Usuario.id == usuario_id).options(selectinload(Usuario.perfil))
    )
    usuario = (await session.exec(consulta)).first()
    if usuario is None or usuario.perfil is None:
        return []
    return [usuario.perfil]


async def crear_perfil_sin_unicidad(
    session: AsyncSession, usuario_id: int, datos: PerfilCreate
) -> PerfilSinUnicidad:
    """El mismo INSERT contra la tabla que NO tiene la restricción."""
    perfil = PerfilSinUnicidad(usuario_id=usuario_id, apodo=datos.apodo)
    session.add(perfil)
    try:
        await session.commit()
    except IntegrityError as error:
        await session.rollback()
        raise rechazo("El perfil apunta a un usuario que no existe.", error) from error
    return perfil


async def perfiles_sin_unicidad_del_usuario(
    session: AsyncSession, usuario_id: int
) -> list[PerfilSinUnicidad]:
    """Los perfiles sin unicidad del usuario, navegando la lista (precargada).

    Acá la relación es una lista: sin `unique=True` nada impide que haya dos.
    """
    consulta = (
        select(Usuario)
        .where(Usuario.id == usuario_id)
        .options(selectinload(Usuario.perfiles_sin_unicidad))
    )
    usuario = (await session.exec(consulta)).first()
    if usuario is None:
        return []
    return sorted(usuario.perfiles_sin_unicidad, key=lambda perfil: perfil.id)


# ═══════════════════════════════════════════════════════════════════════════
# PARTE 2 · CÓMO SE LEEN
# ═══════════════════════════════════════════════════════════════════════════


# ─── diapositiva 11: back_populates, las dos puntas del hilo ────────
async def crear_usuario_con_primer_pedido(
    session: AsyncSession, datos: UsuarioConPrimerPedidoCreate
) -> dict:
    """Se agrega el pedido a la lista del usuario y el ORM completa el resto.

    1) `usuario.pedidos.append(pedido)` toca UNA sola punta del hilo.
    2) `back_populates` completa la otra en memoria: `pedido.usuario` ya es
       el usuario, aunque todavía no se mandó nada a la base.
    3) `pedido.usuario_id` sigue vacío: el número todavía no existe en
       ningún lado. Lo escribe el ORM al guardar, en el INSERT del pedido.

    Lo que se guarda sigue siendo la clave foránea de la Parte 1.
    `Relationship()` no agregó columnas: es una forma de navegar.
    """
    # Ni el usuario ni el pedido traen id: los asigna la base al guardar.
    usuario = Usuario(nombre=datos.nombre)
    pedido = Pedido()
    usuario.pedidos.append(pedido)  # se tira de una punta del hilo...
    antes_de_guardar = {
        "pedido_usuario_es_el_usuario": pedido.usuario is usuario,  # ...y la otra se enteró
        "pedido_usuario_id": pedido.usuario_id,  # el número todavía no está
    }
    session.add(usuario)  # el pedido entra con él: está en su lista
    # Sin ids escritos a mano no hay nada que la base pueda rechazar: el
    # pedido apunta al usuario que se guarda en la misma transacción.
    await session.commit()
    return {"antes_de_guardar": antes_de_guardar, "usuario": usuario, "pedido": pedido}


# ─── diapositiva 12: declarar no es cargar ──────────────────────────
async def que_hay_en_memoria(session: AsyncSession, usuario_id: int) -> dict | None:
    """Trae al usuario y le pregunta al ORM qué atributos tiene cargados.

    `session.get` emite UNA consulta, sólo sobre la tabla usuario. La relación
    `pedidos` está declarada en el modelo, pero en memoria no hay nada: el
    ORM sólo sabe dónde ir a buscarla. La ficha dice «ver depósito».

    `inspect(objeto).unloaded` es la lista de atributos que el ORM todavía no
    fue a buscar a la base.
    """
    usuario = await session.get(Usuario, usuario_id)
    if not usuario:
        return None
    estado = inspect(usuario)
    return {
        "usuario": usuario,
        "atributos_cargados": sorted(set(estado.attrs.keys()) - estado.unloaded),
        "atributos_sin_cargar": sorted(estado.unloaded),
    }


# ─── diapositiva 15: sin precarga (VERSIÓN INCORRECTA, a propósito) ─
async def pedidos_sin_precarga(session: AsyncSession, usuario_id: int) -> list[Pedido] | None:
    """Trae al usuario sin precargar sus pedidos y después toca `usuario.pedidos`.

    En la consola de uvicorn aparece la consulta que el ORM INTENTÓ hacer
    (SELECT ... FROM pedido WHERE ... = pedido.usuario_id): es la consulta de
    la diapositiva 12, la que estaba detrás de `usuario.pedidos`. En
    asincrónico no puede salir fuera de un `await`, y explota MissingGreenlet.

    La excepción se atrapa sólo para devolverla con un mensaje claro: en un
    proyecto real no se atrapa, se arregla precargando (diapositiva 14).
    """
    usuario = await session.get(Usuario, usuario_id)
    if not usuario:
        return None
    try:
        return list(usuario.pedidos)  # <- acá explota: nadie precargó los pedidos
    except MissingGreenlet as error:
        raise HTTPException(
            status_code=500,
            detail={
                "mensaje": (
                    "Versión incorrecta a propósito: se tocó usuario.pedidos sin "
                    "haberlo precargado. Declarar la relación no la carga."
                ),
                "excepcion": "sqlalchemy.exc.MissingGreenlet",
                "mensaje_de_la_excepcion": str(error),
            },
        ) from error


# ─── diapositiva 14: la misma navegación, precargada ────────────────
async def obtener_con_pedidos(session: AsyncSession, usuario_id: int) -> Usuario | None:
    """El usuario con sus pedidos ya en memoria: dos consultas.

    1) SELECT ... FROM usuario WHERE id = 7
    2) SELECT ... FROM pedido WHERE usuario_id IN (7)

    La segunda es la consulta que estaba detrás de `usuario.pedidos`
    (diapositiva 12), emitida ahora a tiempo, dentro del `await`. Como en
    `pedidos/service.py → obtener_con_detalles`, en el TPI esta precarga se
    declara en el repositorio (diapositiva 14).
    """
    consulta = select(Usuario).where(Usuario.id == usuario_id).options(selectinload(Usuario.pedidos))
    return (await session.exec(consulta)).first()
