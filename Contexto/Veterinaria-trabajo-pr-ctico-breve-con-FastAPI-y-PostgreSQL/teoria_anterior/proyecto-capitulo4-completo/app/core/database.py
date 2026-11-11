"""El motor, la sesión y el contador de consultas.

Dos piezas, y conviene no confundirlas:

  - el MOTOR (engine) sabe hablar con PostgreSQL y administra el pool de conexiones. Hay UNO
    para toda la aplicación, creado una sola vez en el ciclo de vida (lifespan de `main.py`):
    ni por petición, ni al importar este archivo.
  - la SESIÓN es la unidad de trabajo de una petición: acumula los cambios y los confirma
    (commit) o los descarta (rollback). Hay una POR PETICIÓN, y la entrega `get_session()`.

El esquema NO se crea acá: lo crea `reiniciar.py`, con `SQLModel.metadata.create_all`, cada vez
que se quiere volver a los datos de las diapositivas.
"""

from collections.abc import AsyncIterator

from fastapi import Request
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlalchemy.orm import ORMExecuteState, Session
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import DATABASE_URL


def crear_motor() -> AsyncEngine:
    """El motor asincrónico. Lo llama UNA vez el lifespan de `main.py` (y `reiniciar.py`)."""
    return create_async_engine(
        DATABASE_URL,
        # echo=True: el motor imprime en la consola cada sentencia SQL que ejecuta de verdad. Es
        # la única manera de responder con certeza "¿el ORM hizo una consulta o cincuenta?". En
        # este capítulo queda prendido: lo que se estudia es qué SQL llega a la base.
        echo=True,
    )


def crear_fabrica_de_sesiones(motor: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """La "fábrica" que produce una sesión por petición.

    expire_on_commit=False NO es una optimización: con el valor por defecto, después de cada
    commit los objetos quedan vencidos y leer `producto.id` obligaría a volver a consultar la
    base; esa consulta implícita ocurriría en una línea común, sin await, y en asincrónico eso
    explota con MissingGreenlet (Capítulo 4, sección 4.5).
    """
    return async_sessionmaker(motor, class_=AsyncSession, expire_on_commit=False)


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    """Dependencia de FastAPI: una sesión nueva por petición, cerrada siempre al terminar.

    La fábrica vive en app.state (la dejó ahí el lifespan). Este archivo no la crea: la usa.
    """
    fabrica: async_sessionmaker[AsyncSession] = request.app.state.fabrica_de_sesiones
    async with fabrica() as session:
        yield session


# ── Parte 2: contar las consultas de cada petición ───────────────────────────────────────────
# `do_orm_execute` es un evento que SQLAlchemy dispara cada vez que una sesión manda una consulta
# a la base: las que escribe el `service` y también las que arma el ORM por su cuenta para una
# precarga (cada `selectinload` es una consulta más). Como cada petición tiene su propia sesión,
# el contador queda guardado en `session.info` y arranca en cero en cada petición.
@event.listens_for(Session, "do_orm_execute")
def _contar_consulta(estado: ORMExecuteState) -> None:
    estado.session.info["consultas"] = estado.session.info.get("consultas", 0) + 1


def consultas_emitidas(session: AsyncSession) -> int:
    """Cuántas consultas mandó esta sesión hasta ahora (diapositivas 13 y 14)."""
    return session.info.get("consultas", 0)
