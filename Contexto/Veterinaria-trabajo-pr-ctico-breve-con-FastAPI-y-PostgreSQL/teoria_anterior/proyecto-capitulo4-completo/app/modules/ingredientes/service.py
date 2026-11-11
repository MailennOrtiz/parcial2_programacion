from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.ingredientes.models import Ingrediente
from app.modules.ingredientes.schemas import IngredienteCreate
from app.modules.productos.models import ProductoIngrediente


async def crear_ingrediente(session: AsyncSession, datos: IngredienteCreate) -> Ingrediente:
    # El id lo asigna la base; no hay nada que pueda rechazar el alta.
    ingrediente = Ingrediente.model_validate(datos)
    session.add(ingrediente)
    await session.commit()
    return ingrediente


async def listar_ingredientes(session: AsyncSession) -> list[Ingrediente]:
    return list((await session.exec(select(Ingrediente).order_by(Ingrediente.id))).all())


# ─── Muchos a muchos, desde el otro lado (diapositiva 6) ───────────────────
async def productos_que_lo_llevan(session: AsyncSession, ingrediente_id: int) -> list[dict]:
    """En qué productos va un ingrediente, NAVEGANDO desde el otro extremo.

    ingrediente.productos     -> las filas de la receta que lo usan
    fila.producto.nombre      -> el producto de cada fila

    Es la misma tabla intermedia que usa `productos.service.receta_del_producto`,
    recorrida en el otro sentido: por eso es "muchos" de los dos lados. Las dos
    navegaciones van precargadas (selectinload encadenado).
    """
    consulta = (
        select(Ingrediente)
        .where(Ingrediente.id == ingrediente_id)
        .options(
            selectinload(Ingrediente.productos).selectinload(ProductoIngrediente.producto)
        )
    )
    ingrediente = (await session.exec(consulta)).first()
    if ingrediente is None:
        return []
    filas = sorted(ingrediente.productos, key=lambda fila: fila.producto_id)
    return [
        {"producto_id": f.producto_id, "producto": f.producto.nombre, "cantidad": f.cantidad}
        for f in filas
    ]
