from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.errores import rechazo
from app.modules.categorias.models import Categoria
from app.modules.categorias.schemas import CategoriaCreate
from app.modules.productos.models import Producto


async def crear_categoria(session: AsyncSession, datos: CategoriaCreate) -> Categoria:
    # El id lo asigna la base. Lo único que puede rechazar el alta es la unicidad del nombre.
    categoria = Categoria.model_validate(datos)
    session.add(categoria)
    try:
        await session.commit()
    except IntegrityError as error:
        await session.rollback()
        raise rechazo("Ya existe una categoría con ese nombre.", error) from error
    return categoria


async def listar_categorias(session: AsyncSession) -> list[Categoria]:
    return list((await session.exec(select(Categoria).order_by(Categoria.id))).all())


async def productos_de_la_categoria(session: AsyncSession, categoria_id: int) -> list[Producto]:
    """Otra vez uno a muchos: se buscan los productos que apuntan a ella."""
    consulta = (
        select(Producto).where(Producto.categoria_id == categoria_id).order_by(Producto.id)
    )
    return list((await session.exec(consulta)).all())


# ─── Agregación (diapositiva 7) ───────────────────────────────────────
async def borrar_categoria(session: AsyncSession, categoria_id: int) -> bool:
    """Intenta borrar la categoría. Qué pasa lo decide la clave foránea de
    `producto.categoria_id`, no este código:

      - ON DELETE RESTRICT -> la base rechaza el borrado si quedan productos.
      - ON DELETE SET NULL -> la categoría se va y los productos quedan con
        `categoria_id` vacío.

    Esta función es la misma en los dos casos. Lo que cambia está en la base.
    """
    categoria = await session.get(Categoria, categoria_id)
    if not categoria:
        return False
    await session.delete(categoria)
    try:
        await session.commit()
    except IntegrityError as error:
        await session.rollback()
        raise rechazo(
            "No se puede borrar la categoría: todavía hay productos que apuntan a ella.", error
        ) from error
    return True
