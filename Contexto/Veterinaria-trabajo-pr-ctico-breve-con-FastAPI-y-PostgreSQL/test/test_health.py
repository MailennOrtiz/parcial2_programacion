"""Pruebas de infraestructura y salud sin necesitar un servidor PostgreSQL."""

import asyncio
import os
import unittest
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.core.config import obtener_database_url
from app.core.database import crear_fabrica_de_sesiones, crear_motor, get_session
from app.main import app


URL_PRUEBA = "postgresql+asyncpg://usuario:ejemplo@127.0.0.1:5432/veterinaria_test"


class ConfigTests(unittest.TestCase):
    def test_url_desde_entorno(self):
        with patch.dict(os.environ, {"DATABASE_URL": URL_PRUEBA}), patch("app.core.config.load_dotenv"):
            self.assertEqual(obtener_database_url(), URL_PRUEBA)

    def test_url_ausente(self):
        with patch.dict(os.environ, {}, clear=True), patch("app.core.config.load_dotenv"):
            with self.assertRaisesRegex(RuntimeError, "Falta DATABASE_URL"):
                obtener_database_url()

    def test_url_invalida_no_expone_secreto(self):
        for valor in ("secreto_invalido", "sqlite:///local.db", "postgresql://u:clave@localhost/db"):
            with self.subTest(valor=valor):
                with patch.dict(os.environ, {"DATABASE_URL": valor}), patch("app.core.config.load_dotenv"):
                    with self.assertRaises(RuntimeError) as contexto:
                        obtener_database_url()
                    self.assertNotIn(valor, str(contexto.exception))


class HealthTests(unittest.TestCase):
    def setUp(self):
        self.motor = AsyncMock()
        self.config = patch("app.main.obtener_database_url", return_value=URL_PRUEBA)
        self.crear = patch("app.main.crear_motor", return_value=self.motor)
        self.config.start()
        self.crear.start()
        self.addCleanup(self.config.stop)
        self.addCleanup(self.crear.stop)
        self.addCleanup(app.dependency_overrides.clear)

    def usar_session(self, session):
        async def reemplazo():
            yield session

        app.dependency_overrides[get_session] = reemplazo

    def test_live_no_pide_session_y_cierra_motor(self):
        async def session_prohibida():
            raise AssertionError("Live no debe pedir una sesión")
            yield  # Hace que la dependencia sea un generador asincrónico.

        app.dependency_overrides[get_session] = session_prohibida
        with TestClient(app) as client:
            self.assertIs(app.state.motor, self.motor)
            self.assertFalse(app.state.fabrica_de_sesiones.kw["expire_on_commit"])
            respuesta = client.get("/health/live")
            self.assertEqual(respuesta.status_code, 200)
            self.assertEqual(respuesta.json(), {"estado": "vivo"})
        self.motor.dispose.assert_awaited_once()

    def test_ready_ejecuta_select_1(self):
        session = AsyncMock()
        self.usar_session(session)
        with TestClient(app) as client:
            respuesta = client.get("/health/ready")
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json(), {"estado": "listo", "base_de_datos": "disponible"})
        session.execute.assert_awaited_once()
        self.assertEqual(str(session.execute.call_args.args[0]), "SELECT 1")

    def test_ready_falla_sin_afectar_live(self):
        for error in (
            OperationalError("SELECT 1", {}, Exception("secreto de la conexión")),
            OSError("Conexión rechazada"),
            TimeoutError(),
        ):
            with self.subTest(error=type(error).__name__):
                self.usar_session(AsyncMock(execute=AsyncMock(side_effect=error)))
                with TestClient(app) as client:
                    respuesta = client.get("/health/ready")
                    self.assertEqual(respuesta.status_code, 503)
                    self.assertEqual(respuesta.json(), {"detail": "La base de datos no está disponible."})
                    self.assertEqual(client.get("/health/live").status_code, 200)

    def test_ready_tiene_limite_de_tiempo(self):
        async def consulta_lenta(*args):
            await asyncio.sleep(1)

        self.usar_session(AsyncMock(execute=AsyncMock(side_effect=consulta_lenta)))
        with patch("app.modules.health.service.TIEMPO_MAXIMO_READY", 0.01):
            with TestClient(app) as client:
                self.assertEqual(client.get("/health/ready").status_code, 503)

    def test_cierra_motor_ante_error(self):
        with self.assertRaisesRegex(RuntimeError, "Fallo de prueba"):
            with TestClient(app):
                raise RuntimeError("Fallo de prueba")
        self.motor.dispose.assert_awaited_once()


class SessionTests(unittest.IsolatedAsyncioTestCase):
    async def test_dependencia_crea_y_cierra_una_session_por_peticion(self):
        motor = crear_motor(URL_PRUEBA)
        try:
            fabrica = crear_fabrica_de_sesiones(motor)
            request = unittest.mock.Mock()
            request.app.state.fabrica_de_sesiones = fabrica
            primera = get_session(request)
            segunda = get_session(request)
            session_1 = await anext(primera)
            session_2 = await anext(segunda)
            try:
                self.assertIsNot(session_1, session_2)
                self.assertFalse(session_1.sync_session.expire_on_commit)
                with patch.object(session_1, "close", wraps=session_1.close) as cerrar:
                    await primera.aclose()
                    cerrar.assert_awaited_once()
            finally:
                await primera.aclose()
                await segunda.aclose()
        finally:
            await motor.dispose()
