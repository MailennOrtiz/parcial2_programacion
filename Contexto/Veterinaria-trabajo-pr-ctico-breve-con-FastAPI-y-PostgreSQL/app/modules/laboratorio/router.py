"""Consulta asincrónica de stock, sin depender de la base de datos."""

from typing import Annotated

from fastapi import APIRouter, Path

from app.modules.laboratorio.schemas import StockRead
from app.modules.laboratorio.service import obtener_stock


router = APIRouter(prefix="/laboratorio", tags=["Laboratorio"])


@router.get("/stock/{vacuna}", response_model=StockRead)
async def stock(vacuna: Annotated[str, Path(min_length=1, max_length=120)]) -> StockRead:
    return await obtener_stock(vacuna)
