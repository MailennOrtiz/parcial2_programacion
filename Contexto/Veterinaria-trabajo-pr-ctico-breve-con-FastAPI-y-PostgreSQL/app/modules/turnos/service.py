"""Reserva todo o nada y lecturas con dos consultas, sin carga perezosa."""

from datetime import timezone
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, raiseload, selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.errores import conflicto
from app.modules.mascotas.schemas import MascotaResumenRead
from app.modules.practicas.models import Practica
from app.modules.turnos.models import Turno, TurnoPractica
from app.modules.turnos.schemas import TurnoCreate, TurnoPracticaRead, TurnoRead


async def obtener_turno(session: AsyncSession, turno_id: int) -> Turno:
    consulta = (
        select(Turno)
        .where(Turno.id == turno_id)
        .options(
            joinedload(Turno.mascota),
            selectinload(Turno.practicas).joinedload(TurnoPractica.practica),
            raiseload("*"),
        )
        # Tras un alta, también precarga los objetos ya presentes en la sesión.
        .execution_options(populate_existing=True)
    )
    turno = (await session.exec(consulta)).first()
    if turno is None:
        raise HTTPException(status_code=404, detail="Turno no encontrado.")
    return turno


def lectura_turno(turno: Turno) -> TurnoRead:
    """Aplana la clase intermedia usando únicamente relaciones ya precargadas."""
    return TurnoRead(
        id=turno.id,
        fecha=turno.fecha,
        motivo=turno.motivo,
        total=turno.total,
        mascota=MascotaResumenRead.model_validate(turno.mascota),
        practicas=[
            TurnoPracticaRead(
                practica_id=linea.practica_id,
                nombre=linea.practica.nombre,
                precio_unitario=linea.precio_unitario,
            )
            for linea in sorted(turno.practicas, key=lambda parte: parte.practica_id)
        ],
    )


async def crear_turno(session: AsyncSession, datos: TurnoCreate) -> TurnoRead:
    # Consulta de datos necesaria para copiar los precios, no un SELECT de existencia.
    # IN puede deduplicar la búsqueda, pero se conserva cada entrada del DTO al insertar:
    # la PK compuesta, no Python, rechaza prácticas repetidas.
    ids = [parte.practica_id for parte in datos.practicas]
    catalogo = (await session.exec(select(Practica.id, Practica.precio).where(Practica.id.in_(ids)))).all()
    precios = dict(catalogo)
    turno = Turno(
        mascota_id=datos.mascota_id,
        fecha=datos.fecha.astimezone(timezone.utc),
        motivo=datos.motivo,
        total=sum((precios.get(id, Decimal("0.00")) for id in ids), Decimal("0.00")),
        practicas=[
            TurnoPractica(
                practica_id=id,
                # Si no está en el catálogo no hay precio que copiar. Se conserva
                # el id y NO se inventa un importe: la base rechaza NULL (NOT NULL),
                # además de tener la FK que garantiza la referencia. Nada se guarda.
                precio_unitario=precios.get(id),
            )
            for id in ids
        ],
    )
    session.add(turno)
    try:
        # Único commit: el turno y todas sus partes pertenecen a esta transacción.
        await session.commit()
    except IntegrityError as error:
        await session.rollback()
        raise conflicto(
            "No se pudo reservar el turno: mascota o práctica inexistente, "
            "o práctica repetida. No se guardó el turno ni sus prácticas."
        ) from error
    return lectura_turno(await obtener_turno(session, turno.id))


async def detalle_turno(session: AsyncSession, turno_id: int) -> TurnoRead:
    return lectura_turno(await obtener_turno(session, turno_id))


async def borrar_turno(session: AsyncSession, turno_id: int) -> None:
    turno = await session.get(Turno, turno_id)
    if turno is None:
        raise HTTPException(status_code=404, detail="Turno no encontrado.")
    try:
        await session.delete(turno)
        await session.commit()
    except IntegrityError as error:
        await session.rollback()
        raise conflicto("La base rechazó el borrado del turno.") from error
