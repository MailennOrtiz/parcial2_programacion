"""Prueba la carga en SQLite en memoria y el flujo async con dobles de prueba.

No usa DATABASE_URL ni se conecta a la base real de veterinaria.
"""

from contextlib import asynccontextmanager
from decimal import Decimal
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, patch

from sqlalchemy import event
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, SQLModel, create_engine, select

from app.core.modelos import Duenio, FichaDuenio, Mascota, Practica, Turno, TurnoPractica
from reiniciar import cargar_datos, reiniciar


class CargaTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.motor = create_engine("sqlite://")

        @event.listens_for(self.motor, "connect")
        def activar_fk(conexion, registro):
            conexion.execute("PRAGMA foreign_keys=ON")

        SQLModel.metadata.create_all(self.motor)
        self.addCleanup(self.motor.dispose)

    async def cargar(self):
        with Session(self.motor) as session:
            # Adaptador para ejecutar la misma carga async sobre una base aislada,
            # sin agregar un controlador SQLite asincrónico a las dependencias.
            adaptador = SimpleNamespace(
                add=session.add, add_all=session.add_all,
                flush=AsyncMock(side_effect=session.flush),
            )
            await cargar_datos(adaptador)
            session.commit()

    async def test_cantidades_e_ids_iniciales(self):
        await self.cargar()
        with Session(self.motor) as session:
            for modelo, cantidad in (
                (Duenio, 2), (FichaDuenio, 1), (Mascota, 3),
                (Practica, 4), (Turno, 1), (TurnoPractica, 2),
            ):
                self.assertEqual(len(session.exec(select(modelo)).all()), cantidad)
            self.assertEqual(session.get(Duenio, 1).email, "ana@example.com")
            self.assertEqual(session.get(Mascota, 1).nombre, "Toby")
            self.assertEqual(session.get(Practica, 3).nombre, "Vacuna antirrábica")

    async def test_precios_copiados_y_total(self):
        await self.cargar()
        with Session(self.motor) as session:
            turno = session.get(Turno, 1)
            self.assertEqual(turno.total, Decimal("27000.00"))
            lineas = session.exec(select(TurnoPractica).order_by(TurnoPractica.practica_id)).all()
            self.assertEqual([linea.precio_unitario for linea in lineas], [Decimal("15000.00"), Decimal("12000.00")])
            practica = session.get(Practica, 1)
            practica.precio = Decimal("20000.00")
            session.commit()
            self.assertEqual(session.get(TurnoPractica, (1, 1)).precio_unitario, Decimal("15000.00"))
            self.assertEqual(session.get(Turno, 1).total, Decimal("27000.00"))

    async def test_ids_nuevos_sin_colision(self):
        await self.cargar()
        with Session(self.motor) as session:
            duenio = Duenio(nombre="Nuevo", email="nuevo@example.com")
            practica = Practica(nombre="Nueva", precio=Decimal("100.00"))
            session.add_all([duenio, practica])
            session.commit()
            self.assertEqual(duenio.id, 3)
            self.assertEqual(practica.id, 5)

    async def test_recrear_y_cargar_es_repetible(self):
        await self.cargar()
        SQLModel.metadata.drop_all(self.motor)
        SQLModel.metadata.create_all(self.motor)
        await self.cargar()
        with Session(self.motor) as session:
            self.assertEqual(session.get(Turno, 1).total, Decimal("27000.00"))
            self.assertEqual(len(session.exec(select(TurnoPractica)).all()), 2)

    async def test_borrado_turno_lo_resuelve_la_base_con_coleccion_cargada(self):
        await self.cargar()
        with Session(self.motor) as session:
            turno = session.get(Turno, 1)
            self.assertEqual(len(turno.practicas), 2)
            session.delete(turno)
            session.commit()
            self.assertEqual(len(session.exec(select(TurnoPractica)).all()), 0)
            self.assertEqual(len(session.exec(select(Practica)).all()), 4)

    async def test_duenio_con_mascotas_no_se_borra(self):
        await self.cargar()
        with Session(self.motor) as session:
            session.delete(session.get(Duenio, 1))
            with self.assertRaises(IntegrityError):
                session.commit()
            session.rollback()
            self.assertIsNotNone(session.get(Duenio, 1))


class ReinicioTests(unittest.IsolatedAsyncioTestCase):
    async def test_ddl_y_carga_comparten_transaccion_y_cierran_motor(self):
        for falla in (False, True):
            with self.subTest(falla=falla):
                conexion = AsyncMock()
                eventos = []

                @asynccontextmanager
                async def transaccion():
                    try:
                        yield conexion
                    except Exception:
                        eventos.append("rollback")
                        raise
                    else:
                        eventos.append("commit")

                motor = Mock(begin=transaccion, dispose=AsyncMock())
                session = AsyncMock()
                session.begin = Mock(return_value=AsyncMock())
                contexto_session = AsyncMock()
                contexto_session.__aenter__.return_value = session
                fabrica = Mock(return_value=contexto_session)
                carga = AsyncMock(side_effect=ValueError("Fallo de carga") if falla else None)
                with (
                    patch("reiniciar.obtener_database_url", return_value="postgresql+asyncpg://u:p@localhost/prueba"),
                    patch("reiniciar.crear_motor", return_value=motor),
                    patch("reiniciar.crear_fabrica_de_sesiones", return_value=fabrica),
                    patch("reiniciar.cargar_datos", carga),
                    patch("builtins.print"),
                ):
                    if falla:
                        with self.assertRaisesRegex(ValueError, "Fallo de carga"):
                            await reiniciar()
                    else:
                        await reiniciar()
                self.assertEqual(conexion.run_sync.await_args_list[0].args[0], SQLModel.metadata.drop_all)
                self.assertEqual(conexion.run_sync.await_args_list[1].args[0], SQLModel.metadata.create_all)
                fabrica.assert_called_once_with(bind=conexion)
                carga.assert_awaited_once_with(session)
                motor.dispose.assert_awaited_once()
                self.assertEqual(eventos, ["rollback" if falla else "commit"])
