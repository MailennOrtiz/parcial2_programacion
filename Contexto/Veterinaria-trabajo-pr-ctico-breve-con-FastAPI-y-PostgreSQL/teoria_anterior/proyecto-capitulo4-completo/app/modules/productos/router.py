"""Rutas de productos.

Orden de las rutas: OJO ACÁ. La ruta fija `/recetas` va ANTES que `/{producto_id}`. FastAPI prueba
las rutas en el orden en que se declaran y usa la primera que coincide: si `/{producto_id}` viniera
primero, `/productos/recetas` intentaría convertir "recetas" en un número y devolvería 422.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.modules.productos import service
from app.modules.productos.schemas import (
    IngredienteDeLaReceta,
    ProductoConCategoriaRead,
    ProductoCreate,
    ProductoRead,
    RecetaCreate,
    RecetaFila,
)

router = APIRouter(prefix="/productos", tags=["productos"])


# ─── Producto · agregación al crear ────────────────────────────────────────
@router.post("/", response_model=ProductoConCategoriaRead, status_code=201)
async def crear_producto(datos: ProductoCreate, session: AsyncSession = Depends(get_session)):
    """Viaja el id de una categoría que ya existe; la vuelta la trae armada.

    Si `categoria_id` no existe, o si ya hay un producto con ese nombre, la base responde con un 409.
    """
    return await service.crear_producto(session, datos)


@router.get("/", response_model=list[ProductoRead])
async def listar_productos(session: AsyncSession = Depends(get_session)):
    return await service.listar_productos(session)


# ─── Muchos a muchos: la receta (diapositiva 6) ────────────────────────────
@router.get("/recetas", response_model=list[RecetaFila])
async def listar_recetas(session: AsyncSession = Depends(get_session)):
    """La tabla intermedia `producto_ingrediente`, sin unir con nada."""
    return await service.listar_recetas(session)


# ─── Un producto puntual ───────────────────────────────────────────────────
@router.get("/{producto_id}", response_model=ProductoRead)
async def obtener_producto(producto_id: int, session: AsyncSession = Depends(get_session)):
    producto = await service.obtener_producto(session, producto_id)
    if not producto:
        raise service.no_encontrado()
    return producto


@router.delete("/{producto_id}", status_code=204)
async def borrar_producto(producto_id: int, session: AsyncSession = Depends(get_session)):
    """Si el producto figura en un pedido o en una receta, la base no deja borrarlo: 409."""
    if not await service.borrar_producto(session, producto_id):
        raise service.no_encontrado()


@router.get("/{producto_id}/ingredientes", response_model=list[IngredienteDeLaReceta])
async def receta_del_producto(producto_id: int, session: AsyncSession = Depends(get_session)):
    """La receta del producto: cada ingrediente con su cantidad en gramos."""
    return await service.receta_del_producto(session, producto_id)


@router.post("/{producto_id}/ingredientes", response_model=RecetaFila, status_code=201)
async def agregar_ingrediente(
    producto_id: int, datos: RecetaCreate, session: AsyncSession = Depends(get_session)
):
    """Agrega un ingrediente a la receta. Repetirlo devuelve 409."""
    return await service.agregar_ingrediente(session, producto_id, datos)


@router.delete("/{producto_id}/ingredientes/{ingrediente_id}", status_code=204)
async def quitar_ingrediente(
    producto_id: int, ingrediente_id: int, session: AsyncSession = Depends(get_session)
):
    if not await service.quitar_ingrediente(session, producto_id, ingrediente_id):
        raise HTTPException(status_code=404, detail="Ese ingrediente no está en la receta")
