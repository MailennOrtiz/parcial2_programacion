"""Simulación del aviso de comprobante de una venta."""

import asyncio
import logging

logger = logging.getLogger("uvicorn.error.libreria.ventas")


async def avisar_comprobante(venta_id: int) -> None:
    await asyncio.sleep(0.5)
    logger.info("Comprobante notificado (simulación) para la venta %s.", venta_id)
