from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, MissingGreenlet
from sqlalchemy.orm import joinedload, selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.errores import rechazo
from app.modules.pedidos.models import DetallePedido, Pedido
from app.modules.pedidos.schemas import DetalleCreate, PedidoCreate
from app.modules.productos.models import Producto
from app.modules.usuarios.models import Usuario


# ─── Clave foránea (diapositiva 4) · asociación y composición ───────
async def crear_pedido(session: AsyncSession, datos: PedidoCreate) -> Pedido:
    """Guarda el pedido y sus líneas. Si algo no existe, lo rechaza LA BASE.

    Acá no hay ningún `if` que verifique que el usuario exista. Se intenta
    escribir, y es la clave foránea la que dice que no (diap. 4).

    En el DTO viajan dos relaciones distintas:
      - asociación: `usuario_id`, el id de un usuario que ya existe.
      - composición: `detalles`, los DATOS de cada línea. Las líneas nacen
        con el pedido: se agregan a `pedido.detalles` y entran a la base con
        él, en la MISMA transacción.

    Todo o nada: si la base rechaza una sola línea (un `producto_id` que no
    existe), el rollback deshace también el pedido y las otras líneas.
    """
    # Sin id: el número del pedido lo asigna la base al guardar.
    pedido = Pedido(usuario_id=datos.usuario_id)
    for linea in datos.detalles:
        # pedido_id no se escribe a mano: el pedido todavía no tiene número.
        # Lo completa el ORM al guardar, por la relación (diap. 11).
        pedido.detalles.append(
            DetallePedido(producto_id=linea.producto_id, cantidad=linea.cantidad)
        )
    session.add(pedido)  # las líneas entran con él: están en su lista
    try:
        await session.commit()
    except IntegrityError as error:
        await session.rollback()
        # El nombre de la restricción dice cuál de las dos claves foráneas se
        # quejó: la del usuario (asociación) o la del producto de una línea.
        if "pedido_usuario_id_fkey" in str(error.orig):
            mensaje = "El pedido apunta a un usuario que no existe."
        else:
            mensaje = (
                "Una línea apunta a un producto que no existe. No se guardó nada: "
                "ni el pedido ni ninguna de sus líneas."
            )
        raise rechazo(mensaje, error) from error
    # La vuelta: el pedido con su usuario y sus líneas, leídos con la precarga
    # declarada (diap. 14). Devolver `pedido` tal cual obligaría a
    # FastAPI a tocar `pedido.usuario` sin precargar: la carga perezosa que en
    # asincrónico explota (diap. 15).
    return await obtener_con_detalles(session, pedido.id)


async def listar_pedidos(session: AsyncSession) -> list[Pedido]:
    return list((await session.exec(select(Pedido).order_by(Pedido.id))).all())


async def listar_pedidos_con_usuario(session: AsyncSession) -> list[dict]:
    """Con el número se llega al dueño: un JOIN escrito a mano.

    SELECT pedido.id, pedido.usuario_id, usuario.nombre
    FROM pedido JOIN usuario ON usuario.id = pedido.usuario_id
    """
    consulta = (
        select(Pedido.id, Pedido.usuario_id, Usuario.nombre)
        .join(Usuario, Usuario.id == Pedido.usuario_id)
        .order_by(Pedido.id)
    )
    filas = (await session.exec(consulta)).all()
    return [{"id": f[0], "usuario_id": f[1], "usuario": f[2]} for f in filas]


async def obtener_pedido(session: AsyncSession, pedido_id: int) -> Pedido | None:
    return await session.get(Pedido, pedido_id)


# ─── Composición (diapositiva 7) ───────────────────────────────
async def borrar_pedido(session: AsyncSession, pedido_id: int) -> bool:
    """Borra SÓLO el pedido. Las líneas las borra la base (ON DELETE CASCADE).

    Mirá la consola de uvicorn: sale un único DELETE FROM pedido. Nadie
    emite un DELETE sobre detalle_pedido, y sin embargo las líneas se van.
    """
    pedido = await session.get(Pedido, pedido_id)
    if not pedido:
        return False
    await session.delete(pedido)
    await session.commit()
    return True


async def listar_detalles(
    session: AsyncSession, pedido_id: int | None = None, detalle_id: int | None = None
) -> list[dict]:
    """Las líneas, con el nombre del producto (otro JOIN escrito a mano)."""
    consulta = (
        select(
            DetallePedido.id,
            DetallePedido.pedido_id,
            DetallePedido.producto_id,
            Producto.nombre,
            DetallePedido.cantidad,
        )
        .join(Producto, Producto.id == DetallePedido.producto_id)
        .order_by(DetallePedido.id)
    )
    if pedido_id is not None:
        consulta = consulta.where(DetallePedido.pedido_id == pedido_id)
    if detalle_id is not None:
        consulta = consulta.where(DetallePedido.id == detalle_id)
    filas = (await session.exec(consulta)).all()
    return [
        {"id": f[0], "pedido_id": f[1], "producto_id": f[2], "producto": f[3], "cantidad": f[4]}
        for f in filas
    ]


async def agregar_detalle(session: AsyncSession, pedido_id: int, datos: DetalleCreate) -> dict:
    detalle = DetallePedido(pedido_id=pedido_id, **datos.model_dump())
    session.add(detalle)
    try:
        await session.commit()
    except IntegrityError as error:
        await session.rollback()
        raise rechazo("La línea apunta a un pedido o a un producto que no existe.", error) from error
    return (await listar_detalles(session, detalle_id=detalle.id))[0]


# ═══════════════════════════════════════════════════════════════════════════
# PARTE 2 · CÓMO SE LEEN
# ═══════════════════════════════════════════════════════════════════════════
# Desde acá los modelos tienen `Relationship()`: se puede escribir
# `pedido.detalles` o `pedido.usuario`. La pregunta de la Parte 2 es qué
# consultas hay detrás de cada una de esas navegaciones, y cuándo se emiten.
# El router agrega a cada respuesta `consultas_emitidas` (ver core/database.py).


# ─── diapositiva 13: el N+1 (VERSIÓN INCORRECTA, a propósito) ───────
async def listar_con_detalles_n_mas_1(session: AsyncSession) -> list[dict]:
    """Una consulta para los pedidos y después UNA MÁS POR CADA PEDIDO.

    Es lo que hace en silencio un backend sincrónico cuando, dentro de un
    `for`, se escribe `pedido.detalles` sin haberlo precargado: cada acceso es
    un viaje a la base. Acá, en asincrónico, ese acceso explotaría (diap. 15),
    así que la consulta de cada vuelta está escrita a mano para que se vea.

    Con los 3 pedidos de ejemplo: 1 + 3 = 4 consultas.
    Con 100 pedidos serían 1 + 100 = 101, donde alcanzaba con 2.
    """
    pedidos = (await session.exec(select(Pedido).order_by(Pedido.id))).all()  # 1 consulta
    resultado = []
    for pedido in pedidos:  # + 1 consulta por cada pedido: el mandado de a uno
        consulta = (
            select(DetallePedido)
            .where(DetallePedido.pedido_id == pedido.id)
            .order_by(DetallePedido.id)
        )
        lineas = (await session.exec(consulta)).all()
        resultado.append({"id": pedido.id, "usuario_id": pedido.usuario_id, "detalles": lineas})
    return resultado


# ─── diapositiva 15: sin precarga (VERSIÓN INCORRECTA, a propósito) ─
async def obtener_sin_precarga(session: AsyncSession, pedido_id: int) -> list[DetallePedido]:
    """Trae el pedido SIN precargar sus líneas y después las toca.

    `session.get` trae sólo la fila del pedido. Al tocar `pedido.detalles`, el
    ORM intenta ir a buscar las líneas en ese momento (carga perezosa). En un
    backend asincrónico eso no está permitido: la consulta tendría que salir
    fuera del `await` que la haría válida, y SQLAlchemy lanza MissingGreenlet.

    Mirá la consola de uvicorn: aparece la consulta que el ORM INTENTÓ hacer
    (SELECT ... FROM detalle_pedido WHERE ... = detalle_pedido.pedido_id).
    Esa es la consulta escondida detrás de `pedido.detalles`.

    La excepción se atrapa sólo para devolverla con un mensaje claro: en un
    proyecto real no se atrapa, se arregla precargando (diapositiva 14).
    """
    pedido = await session.get(Pedido, pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    try:
        return list(pedido.detalles)  # <- acá explota: nadie precargó las líneas
    except MissingGreenlet as error:
        raise HTTPException(
            status_code=500,
            detail={
                "mensaje": (
                    "Versión incorrecta a propósito: se tocó pedido.detalles sin "
                    "haberlo precargado. Declarar la relación no la carga."
                ),
                "excepcion": "sqlalchemy.exc.MissingGreenlet",
                "mensaje_de_la_excepcion": str(error),
            },
        ) from error


# ─── diapositiva 14: la precarga ───────────────────────────────
async def obtener_con_detalles(session: AsyncSession, pedido_id: int) -> Pedido | None:
    """El pedido con sus líneas y su usuario, ya en memoria.

    Es el código de la diapositiva 14. Las dos líneas de `selectinload`
    DECLARAN qué relaciones va a necesitar la respuesta: sin ellas, acceder a
    `pedido.detalles` lanza la excepción de la diapositiva 15. Cada
    `selectinload` es una consulta más: este método emite tres (el pedido,
    sus líneas, su usuario).

    Diapositiva 14: en el TPI este método vive en el REPOSITORIO (por eso en la
    diapositiva dice `self.session`): es el único que sabe cómo se traen los
    datos, y la precarga se declara ahí. Este proyecto no tiene capa de
    repositorio, así que va en el service, que es quien habla con la base.
    Cuando una excepción de greenlet explote, se mira el método que trajo el
    objeto: le falta una línea.
    """
    consulta = (
        select(Pedido)
        .where(Pedido.id == pedido_id)
        .options(
            selectinload(Pedido.detalles),
            selectinload(Pedido.usuario),
        )
    )
    return (await session.exec(consulta)).first()


async def listar_con_detalles_selectinload(session: AsyncSession) -> list[Pedido]:
    """Todos los pedidos con sus líneas, con `selectinload`: dos consultas.

    1) SELECT ... FROM pedido
    2) SELECT ... FROM detalle_pedido WHERE pedido_id IN (101, 102, 103)

    Cada pedido viaja una sola vez. Es la estrategia para colecciones (uno a
    muchos), como las líneas de un pedido (diapositiva 14).
    """
    consulta = select(Pedido).options(selectinload(Pedido.detalles)).order_by(Pedido.id)
    return list((await session.exec(consulta)).all())


# ─── diapositiva 14: joinedload, y lo que viaja en el JOIN ──────────
async def listar_con_detalles_joinedload(session: AsyncSession) -> list[Pedido]:
    """Los mismos pedidos con sus líneas, con `joinedload`: UNA consulta.

    SELECT ... FROM pedido LEFT OUTER JOIN detalle_pedido ON ...

    `.unique()` es obligatorio cuando se hace joinedload de una colección:
    el JOIN devuelve una fila por línea, así que el pedido 101 llega dos
    veces, y SQLAlchemy exige que se pida explícitamente quedarse con un
    objeto por pedido (sin `.unique()` lanza InvalidRequestError). Que en
    Python quede un solo pedido no cambia lo que viajó por la red: los datos
    del pedido, repetidos una vez por línea (ver `filas_del_join`).
    """
    consulta = select(Pedido).options(joinedload(Pedido.detalles)).order_by(Pedido.id)
    return list((await session.exec(consulta)).unique().all())


async def filas_del_join(session: AsyncSession) -> list[dict]:
    """Las filas crudas del JOIN: lo que `joinedload` recibe de la base.

    Es la misma forma de consulta que arma joinedload (comparala en la
    consola). El pedido 101 aparece una vez por cada línea, y el 103, que no
    tiene líneas, aparece una vez con los campos de la línea vacíos porque el
    JOIN es externo. Con veinte líneas, los datos del pedido viajarían veinte
    veces: «la fotocopia del encabezado».
    """
    consulta = (
        select(
            Pedido.id,
            Pedido.usuario_id,
            DetallePedido.id,
            DetallePedido.producto_id,
            DetallePedido.cantidad,
        )
        .outerjoin(DetallePedido, DetallePedido.pedido_id == Pedido.id)
        .order_by(Pedido.id, DetallePedido.id)
    )
    filas = (await session.exec(consulta)).all()
    return [
        {"pedido_id": f[0], "usuario_id": f[1], "linea_id": f[2], "producto_id": f[3], "cantidad": f[4]}
        for f in filas
    ]
