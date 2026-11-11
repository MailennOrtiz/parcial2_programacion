from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def health_check():
    return {"status": "ok"}


@router.get("/db")
async def db_check(request: Request):
    try:
        async with request.app.state.motor.connect() as conexion:
            await conexion.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as error:  # noqa: BLE001 — se informa cualquier falla de conexión
        # 503 y no 200: el servidor anda, pero sin base no puede atender. Sólo el
        # tipo de error: el mensaje completo puede traer la dirección de la base, y
        # eso no se le manda al cliente.
        return JSONResponse(
            status_code=503, content={"status": "error", "database": type(error).__name__}
        )
