"""La biblioteca bloqueante se ejecuta fuera del bucle de eventos."""

import asyncio

from app.modules.laboratorio import cliente
from app.modules.laboratorio.schemas import StockRead


async def obtener_stock(vacuna: str) -> StockRead:
    stock = await asyncio.to_thread(cliente.consultar_stock, vacuna)
    return StockRead(vacuna=vacuna, stock=stock)
