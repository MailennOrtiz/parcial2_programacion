"""Recrea las tablas del TP y carga datos iniciales. Elimina los datos existentes."""

import asyncio
from datetime import datetime
from decimal import Decimal
import sys

from asyncpg import PostgresError
from sqlalchemy.engine import make_url
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import obtener_database_url
from app.core.database import crear_fabrica_de_sesiones, crear_motor
from app.core.modelos import Duenio, FichaDuenio, Mascota, Practica, Turno, TurnoPractica


async def cargar_datos(session: AsyncSession) -> None:
    """Carga datos fijos sin confirmar: la transacción pertenece al llamador."""
    duenios = [
        Duenio(nombre="Ana García", email="ana@example.com"),
        Duenio(nombre="Luis Pérez", email="luis@example.com"),
    ]
    session.add_all(duenios)
    await session.flush()

    # Los ids los asigna la base: no se insertan ids explícitos que desfasen secuencias.
    session.add(FichaDuenio(
        duenio_id=duenios[0].id, telefono="1155550101", direccion="San Martín 123"
    ))
    mascotas = [
        Mascota(nombre="Toby", especie="perro", duenio_id=duenios[0].id),
        Mascota(nombre="Mora", especie="gato", duenio_id=duenios[0].id),
        Mascota(nombre="Luna", especie="perro", duenio_id=duenios[1].id),
    ]
    session.add_all(mascotas)
    await session.flush()

    practicas = [
        Practica(nombre="Consulta", precio=Decimal("15000.00")),
        Practica(nombre="Desparasitación", precio=Decimal("8000.00")),
        Practica(nombre="Vacuna antirrábica", precio=Decimal("12000.00")),
        Practica(nombre="Corte de uñas", precio=Decimal("5000.00")),
    ]
    session.add_all(practicas)
    await session.flush()

    reservadas = [practicas[0], practicas[2]]
    turno = Turno(
        mascota_id=mascotas[0].id,
        fecha=datetime.fromisoformat("2026-11-12T10:30:00-03:00"),
        motivo="Control anual",
        total=sum((practica.precio for practica in reservadas), Decimal("0.00")),
        practicas=[
            TurnoPractica(practica_id=practica.id, precio_unitario=practica.precio)
            for practica in reservadas
        ],
    )
    session.add(turno)
    await session.flush()


async def reiniciar() -> None:
    database_url = obtener_database_url()
    print(f"ATENCIÓN: se eliminarán los datos de las tablas del TP en {make_url(database_url).database}.")
    motor = crear_motor(database_url)
    try:
        # PostgreSQL permite DDL transaccional: si falla la carga, también se
        # deshace la recreación del esquema. No usar DROP ... CASCADE ni borrar la base.
        async with motor.begin() as conexion:
            await conexion.run_sync(SQLModel.metadata.drop_all)
            await conexion.run_sync(SQLModel.metadata.create_all)
            fabrica = crear_fabrica_de_sesiones(motor)
            async with fabrica(bind=conexion) as session:
                async with session.begin():
                    await cargar_datos(session)
        print("Base reiniciada: 2 dueños, 1 ficha, 3 mascotas, 4 prácticas y 1 turno con 2 prácticas.")
    finally:
        await motor.dispose()


def main() -> int:
    try:
        asyncio.run(reiniciar())
    except RuntimeError as error:
        # Los errores de configuración tienen mensajes propios sin credenciales.
        print(str(error), file=sys.stderr)
        return 1
    except (SQLAlchemyError, PostgresError, OSError, TimeoutError):
        print(
            "No se pudo reiniciar la base. Revisá la conexión, los permisos y las "
            "dependencias externas sobre las tablas del TP. La transacción se deshizo.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
