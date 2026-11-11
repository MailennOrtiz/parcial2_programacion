from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.modules.categorias import service
from app.modules.categorias.schemas import CategoriaCreate, CategoriaRead
from app.modules.productos.schemas import ProductoRead

router = APIRouter(prefix="/categorias", tags=["categorias"])


@router.post("/", response_model=CategoriaRead, status_code=201)
async def crear_categoria(datos: CategoriaCreate, session: AsyncSession = Depends(get_session)):
    return await service.crear_categoria(session, datos)


@router.get("/", response_model=list[CategoriaRead])
async def listar_categorias(session: AsyncSession = Depends(get_session)):
    return await service.listar_categorias(session)


@router.get("/{categoria_id}/productos", response_model=list[ProductoRead])
async def productos_de_la_categoria(
    categoria_id: int, session: AsyncSession = Depends(get_session)
):
    return await service.productos_de_la_categoria(session, categoria_id)


# ─── Agregación (diapositiva 7) ───────────────────────────────────────
@router.delete("/{categoria_id}", status_code=204)
async def borrar_categoria(categoria_id: int, session: AsyncSession = Depends(get_session)):
    """Con RESTRICT devuelve 409 si tiene productos; con SET NULL la borra."""
    if not await service.borrar_categoria(session, categoria_id):
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
