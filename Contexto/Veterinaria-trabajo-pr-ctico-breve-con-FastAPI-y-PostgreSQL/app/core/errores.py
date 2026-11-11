"""Respuestas propias para conflictos de escritura, sin exponer errores SQL."""

from fastapi import HTTPException, status


def conflicto(mensaje: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=mensaje)
