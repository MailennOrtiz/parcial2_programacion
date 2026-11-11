"""Cuando la base dice que no.

Ningún `service` verifica nada antes de escribir: se intenta, y decide la restricción (la clave
foránea, la unicidad, el CHECK). Cuando la base rechaza la escritura, el `service` atrapa el
`IntegrityError`, deshace la transacción y responde 409 con `rechazo()`.

La respuesta trae, además del mensaje propio, `mensaje_de_la_base`: el texto crudo de PostgreSQL,
con el nombre de la restricción que habló. Se manda a propósito, porque ver qué contestó la base
es lo que se estudia en este capítulo.
"""

import logging

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

log = logging.getLogger("uvicorn.error")

# Los códigos con que PostgreSQL dice qué restricción se violó (SQLSTATE).
CLAVE_FORANEA = "23503"
UNICIDAD = "23505"


def codigo_de(error: IntegrityError) -> str | None:
    """El SQLSTATE del rechazo: dice si fue la clave foránea, la unicidad o un CHECK."""
    return getattr(error.orig, "sqlstate", None)


def rechazo(mensaje: str, error: IntegrityError) -> HTTPException:
    """El 409 con el mensaje propio y, al lado, lo que dijo la base."""
    log.warning("La base rechazó la escritura: %s", error.orig)
    return HTTPException(
        status_code=409, detail={"mensaje": mensaje, "mensaje_de_la_base": str(error.orig)}
    )
