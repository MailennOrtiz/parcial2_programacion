from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.errores import CLAVE_FORANEA, UNICIDAD, codigo_de, rechazo
from app.modules.productos.models import Producto, ProductoIngrediente
from app.modules.productos.schemas import ProductoCreate, RecetaCreate


# ─── Producto · agregación al crear (diapositiva 7) y unicidad (diapositiva 18) ──
async def crear_producto(session: AsyncSession, datos: ProductoCreate) -> Producto:
    """Guarda el producto. En el DTO viaja el id de una categoría que ya existe.

    Agregación: la categoría no se crea ni se toca, el producto sólo la nombra por su id. Si ese
    id no existe, lo rechaza LA BASE (409).

    Diapositiva 18, la ventana entre preguntar y escribir: este método NO hace un SELECT previo
    para "fijarse si ya existe" un producto con ese nombre. Esa pregunta y el INSERT que sigue no
    son atómicos entre sí, y dos peticiones simultáneas pueden pasar la pregunta antes de que
    ninguna haya escrito. La única defensa real es que la base rechace la segunda escritura, y
    capturar ese rechazo acá (scripts/demo_unicidad.py).
    """
    producto = Producto.model_validate(datos)
    session.add(producto)
    try:
        await session.commit()
    except IntegrityError as error:
        # Sin el rollback la sesión queda rota (PendingRollbackError) y no se puede volver a usar.
        await session.rollback()
        if codigo_de(error) == UNICIDAD:
            raise rechazo(f"Ya existe un producto llamado '{datos.nombre}'.", error) from error
        raise rechazo("El producto apunta a una categoría que no existe.", error) from error
    # La vuelta: el producto con su categoría, ya en memoria. Es una relación
    # «a uno», así que la precarga es joinedload: una sola consulta con JOIN
    # (diapositiva 14). populate_existing: el objeto ya está en la sesión con el
    # precio tal como llegó (4500); así se pisa con lo que guardó la base (4500.00).
    consulta = (
        select(Producto)
        .where(Producto.id == producto.id)
        .options(joinedload(Producto.categoria))
        .execution_options(populate_existing=True)
    )
    return (await session.exec(consulta)).first()


async def listar_productos(session: AsyncSession) -> list[Producto]:
    """Los productos, tal cual están guardados."""
    consulta = select(Producto).order_by(Producto.id)
    return list((await session.exec(consulta)).all())


async def obtener_producto(session: AsyncSession, producto_id: int) -> Producto | None:
    return await session.get(Producto, producto_id)


async def borrar_producto(session: AsyncSession, producto_id: int) -> bool:
    """Borra el producto, si nada lo nombra. Lo decide la base: las líneas de pedido y las recetas
    apuntan al producto con claves foráneas sin ON DELETE, que rechazan el borrado."""
    producto = await session.get(Producto, producto_id)
    if not producto:
        return False
    await session.delete(producto)
    try:
        await session.commit()
    except IntegrityError as error:
        await session.rollback()
        raise rechazo(
            "No se puede borrar el producto: figura en pedidos o en recetas.", error
        ) from error
    return True


# ─── Muchos a muchos: la receta (diapositiva 6) ────────────────────────────
async def listar_recetas(session: AsyncSession) -> list[ProductoIngrediente]:
    """La tabla intermedia, tal cual está guardada: dos claves y un dato propio."""
    consulta = select(ProductoIngrediente).order_by(
        ProductoIngrediente.producto_id, ProductoIngrediente.ingrediente_id
    )
    return list((await session.exec(consulta)).all())


async def receta_del_producto(session: AsyncSession, producto_id: int) -> list[dict]:
    """Los ingredientes de un producto, con su cantidad, NAVEGANDO la relación.

    producto.ingredientes          -> las filas de la receta (ProductoIngrediente)
    fila.ingrediente.nombre        -> el ingrediente de cada fila
    fila.cantidad                  -> el dato propio de la relación

    Las dos navegaciones se precargan en la misma consulta del producto, con
    `selectinload` encadenado (diapositiva 14): en la consola
    salen tres SELECT (producto, producto_ingrediente, ingrediente), el
    segundo y el tercero con `IN (...)`. Sin esa línea, tocar
    `producto.ingredientes` lanzaría MissingGreenlet (diapositiva 15).

    La cantidad sale de la tabla del medio: no está en producto ni en
    ingrediente.
    """
    consulta = (
        select(Producto)
        .where(Producto.id == producto_id)
        .options(
            selectinload(Producto.ingredientes).selectinload(ProductoIngrediente.ingrediente)
        )
    )
    producto = (await session.exec(consulta)).first()
    if producto is None:
        return []
    filas = sorted(producto.ingredientes, key=lambda fila: fila.ingrediente_id)
    return [
        {"ingrediente_id": f.ingrediente_id, "ingrediente": f.ingrediente.nombre, "cantidad": f.cantidad}
        for f in filas
    ]


async def agregar_ingrediente(
    session: AsyncSession, producto_id: int, datos: RecetaCreate
) -> ProductoIngrediente:
    """Agrega una fila a la tabla intermedia. Ni `producto` ni `ingrediente`
    se modifican: la relación entera vive en la tabla del medio.

    Repetir el mismo ingrediente en el mismo producto lo rechaza la clave
    primaria compuesta (producto_id, ingrediente_id).
    """
    fila = ProductoIngrediente(producto_id=producto_id, **datos.model_dump())
    session.add(fila)
    try:
        await session.commit()
    except IntegrityError as error:
        await session.rollback()
        if codigo_de(error) == CLAVE_FORANEA:
            mensaje = "La receta apunta a un producto o a un ingrediente que no existe."
        else:
            mensaje = "Ese ingrediente ya está en la receta de ese producto."
        raise rechazo(mensaje, error) from error
    return fila


async def quitar_ingrediente(session: AsyncSession, producto_id: int, ingrediente_id: int) -> bool:
    fila = await session.get(ProductoIngrediente, (producto_id, ingrediente_id))
    if not fila:
        return False
    await session.delete(fila)
    await session.commit()
    return True


def no_encontrado() -> HTTPException:
    return HTTPException(status_code=404, detail="Producto no encontrado")
