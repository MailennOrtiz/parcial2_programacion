"""Deja la base como en las diapositivas. Se puede correr las veces que haga falta.

    python reiniciar.py

  1. Crea la base si todavía no existe.
  2. Borra TODAS las tablas, con lo que se haya cambiado a mano con los
     archivos .sql de `test/` (la regla SET NULL de la diapositiva 7, el índice y los 60.000
     pedidos de la diapositiva 8).
  3. Vuelve a crear las tablas a partir de los modelos, con `SQLModel.metadata.create_all`.
  4. Carga los datos de las diapositivas, con los ids de los diagramas.

No hace falta apagar el servidor: las conexiones que tiene en su pool no bloquean nada.
"""

import asyncio
from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

import app.core.modelos  # noqa: F401  (registra todas las tablas en SQLModel.metadata)
from app.core.config import DATABASE_URL
from app.modules.categorias.models import Categoria
from app.modules.ingredientes.models import Ingrediente
from app.modules.pedidos.models import DetallePedido, Pedido
from app.modules.productos.models import Producto, ProductoIngrediente
from app.modules.usuarios.models import Perfil, PerfilSinUnicidad, Usuario

# Tablas con `id` autonumérico: después de cargar ids escritos a mano hay que avisarle al contador
# de cada una desde dónde seguir (el próximo pedido es el 104, el próximo usuario el 9...).
TABLAS_CON_ID = (
    "usuario", "perfil", "perfil_sin_unicidad", "categoria", "producto",
    "pedido", "detalle_pedido", "ingrediente",
)  # fmt: skip


def datos_de_las_diapositivas() -> list[list]:
    """Los mismos de los diagramas. El orden importa: primero las filas a las que otras apuntan."""
    return [
        [Usuario(id=7, nombre="Marta"), Usuario(id=8, nombre="Rubén")],
        [
            Categoria(id=1, nombre="Comidas"),
            Categoria(id=2, nombre="Bebidas"),
            Categoria(id=3, nombre="Golosinas"),
        ],
        [
            Producto(id=1, nombre="Empanada", precio=Decimal("1200.00"), costo_interno=Decimal("700.00"), categoria_id=1),
            Producto(id=2, nombre="Gaseosa", precio=Decimal("2500.00"), costo_interno=Decimal("1500.00"), categoria_id=2),
            Producto(id=3, nombre="Alfajor", precio=Decimal("900.00"), costo_interno=Decimal("400.00"), categoria_id=3),
        ],
        [
            Pedido(id=101, usuario_id=7),
            Pedido(id=102, usuario_id=7),
            Pedido(id=103, usuario_id=8),
        ],
        [
            DetallePedido(id=1, pedido_id=101, producto_id=1, cantidad=3),
            DetallePedido(id=2, pedido_id=101, producto_id=2, cantidad=1),
            DetallePedido(id=3, pedido_id=102, producto_id=3, cantidad=6),
        ],
        [Ingrediente(id=1, nombre="Cebolla"), Ingrediente(id=2, nombre="Carne")],
        [
            ProductoIngrediente(producto_id=1, ingrediente_id=1, cantidad=50),
            ProductoIngrediente(producto_id=1, ingrediente_id=2, cantidad=120),
        ],
        [Perfil(id=1, usuario_id=7, apodo="Martita")],
        [PerfilSinUnicidad(id=1, usuario_id=7, apodo="Martita")],
    ]


async def crear_base_si_falta() -> None:
    """Crea la base del proyecto la primera vez, para no hacerlo a mano."""
    url = make_url(DATABASE_URL)
    mantenimiento = create_async_engine(url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    try:
        async with mantenimiento.connect() as conexion:
            existe = await conexion.scalar(
                text("SELECT 1 FROM pg_database WHERE datname = :nombre"), {"nombre": url.database}
            )
            if not existe:
                await conexion.execute(text(f'CREATE DATABASE "{url.database}"'))
                print(f"Base creada: {url.database}")
    finally:
        await mantenimiento.dispose()


async def borrar_tablas() -> None:
    motor = create_async_engine(DATABASE_URL)
    try:
        async with motor.begin() as conexion:
            tablas = (await conexion.execute(
                text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
            )).scalars().all()
            for tabla in tablas:
                await conexion.execute(text(f'DROP TABLE IF EXISTS "{tabla}" CASCADE'))
    finally:
        await motor.dispose()


async def crear_tablas() -> None:
    """Crea las tablas de todos los modelos: claves foráneas, CHECK, índices y unicidades."""
    motor = create_async_engine(DATABASE_URL)
    try:
        async with motor.begin() as conexion:
            await conexion.run_sync(SQLModel.metadata.create_all)
    finally:
        await motor.dispose()


async def cargar_datos() -> None:
    motor = create_async_engine(DATABASE_URL)
    sesiones = async_sessionmaker(motor, class_=AsyncSession, expire_on_commit=False)
    try:
        async with sesiones() as session:
            for tanda in datos_de_las_diapositivas():
                session.add_all(tanda)
                await session.flush()
            for tabla in TABLAS_CON_ID:
                await session.exec(text(  # type: ignore[call-overload]
                    f"SELECT setval(pg_get_serial_sequence('{tabla}', 'id'), (SELECT max(id) FROM {tabla}))"
                ))
            await session.commit()
    finally:
        await motor.dispose()


async def main() -> None:
    await crear_base_si_falta()
    await borrar_tablas()
    await crear_tablas()
    await cargar_datos()
    print("Listo: la base quedó como en las diapositivas. Usuarios 7 y 8, pedidos 101 a 103, "
          "productos 1 a 3 y la receta de la empanada.")


if __name__ == "__main__":
    asyncio.run(main())
