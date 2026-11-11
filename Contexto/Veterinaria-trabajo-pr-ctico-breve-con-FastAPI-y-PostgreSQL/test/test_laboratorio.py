"""Stock y concurrencia en el mismo bucle de eventos, sin base de datos."""

import asyncio
import inspect
import threading
import time
import unittest
from unittest.mock import AsyncMock, patch

from fastapi import FastAPI
from fastapi.routing import APIRoute
from httpx import ASGITransport, AsyncClient

from app.core.database import get_session
from app.main import (
    app as app_real, duenios_router, health_router, laboratorio_router,
    mascotas_router, practicas_router, turnos_router,
)
from app.modules.laboratorio import cliente
from app.modules.laboratorio.service import obtener_stock
from c09_concurrencia import comprobar


class LaboratorioTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.app = FastAPI()
        self.app.include_router(health_router)
        self.app.include_router(laboratorio_router)

        async def session_prohibida():
            raise AssertionError("Stock y live no deben abrir una sesión")
            yield

        self.app.dependency_overrides[get_session] = session_prohibida
        self.client = AsyncClient(transport=ASGITransport(app=self.app), base_url="http://prueba")
        self.addAsyncCleanup(self.client.aclose)

    async def test_stock_real_y_tres_consultas_simultaneas(self):
        vacunas = ["rabia", "triple", "antirrábica"]
        respuestas = await asyncio.gather(
            *(self.client.get(f"/laboratorio/stock/{vacuna}") for vacuna in vacunas)
        )
        for vacuna, respuesta in zip(vacunas, respuestas):
            self.assertEqual(respuesta.status_code, 200)
            self.assertEqual(respuesta.json(), {"vacuna": vacuna, "stock": 10 + len(vacuna)})

    async def test_service_delega_funcion_original_a_to_thread(self):
        with patch("app.modules.laboratorio.service.asyncio.to_thread", new_callable=AsyncMock, return_value=15) as hilo:
            respuesta = await obtener_stock("rabia")
        hilo.assert_awaited_once_with(cliente.consultar_stock, "rabia")
        self.assertEqual(respuesta.model_dump(), {"vacuna": "rabia", "stock": 15})

    async def test_live_responde_mientras_tres_consultas_siguen_en_curso(self):
        # Barrera explícita: health no se consulta hasta que los tres workers están
        # dentro de la función bloqueante. No depende de adivinar un sleep inicial.
        loop = asyncio.get_running_loop()
        hilo_eventos = threading.get_ident()
        lock = threading.Lock()
        liberar = threading.Event()
        tres_iniciadas = asyncio.Event()
        hilos = []

        def consulta_bloqueada(vacuna):
            with lock:
                hilos.append(threading.get_ident())
                if len(hilos) == 3:
                    loop.call_soon_threadsafe(tres_iniciadas.set)
            if not liberar.wait(timeout=3):
                raise TimeoutError("Las consultas no fueron liberadas por la prueba")
            return 10 + len(vacuna)

        with patch("app.modules.laboratorio.cliente.consultar_stock", side_effect=consulta_bloqueada):
            tareas = [asyncio.create_task(self.client.get(f"/laboratorio/stock/{v}")) for v in ("rabia", "triple", "vacuna")]
            try:
                await asyncio.wait_for(tres_iniciadas.wait(), timeout=1)
                respuesta = await asyncio.wait_for(self.client.get("/health/live"), timeout=0.5)
                self.assertEqual(respuesta.status_code, 200)
                self.assertEqual(respuesta.json(), {"estado": "vivo"})
                self.assertTrue(all(not tarea.done() for tarea in tareas))
                self.assertTrue(all(hilo != hilo_eventos for hilo in hilos))
            finally:
                liberar.set()
                respuestas = await asyncio.gather(*tareas, return_exceptions=True)
            self.assertTrue(all(not isinstance(respuesta, BaseException) for respuesta in respuestas))
            self.assertTrue(all(respuesta.status_code == 200 for respuesta in respuestas))

    async def test_ruta_registrada_en_app_real(self):
        self.assertIn("/laboratorio/stock/{vacuna}", app_real.openapi()["paths"])

    async def test_todos_los_handlers_son_async(self):
        cantidad = 0
        for router in (health_router, duenios_router, mascotas_router, practicas_router, turnos_router, laboratorio_router):
            for ruta in router.routes:
                if isinstance(ruta, APIRoute):
                    cantidad += 1
                    self.assertTrue(inspect.iscoroutinefunction(ruta.endpoint), ruta.path)
        self.assertEqual(cantidad, 17)

    async def test_parametro_demasiado_largo_no_llama_laboratorio(self):
        with patch("app.modules.laboratorio.cliente.consultar_stock") as consulta:
            respuesta = await self.client.get("/laboratorio/stock/" + "v" * 121)
        self.assertEqual(respuesta.status_code, 422)
        consulta.assert_not_called()

    async def test_script_c09_con_peticiones_reales_sobre_asgi(self):
        def stock_lento(vacuna):
            time.sleep(0.3)
            return 10 + len(vacuna)

        def cliente_asgi(**kwargs):
            return AsyncClient(transport=ASGITransport(app=self.app), **kwargs)

        with (
            patch("c09_concurrencia.httpx.AsyncClient", side_effect=cliente_asgi),
            patch("app.modules.laboratorio.cliente.consultar_stock", side_effect=stock_lento),
            patch("builtins.print") as salida,
        ):
            await comprobar("http://prueba", limite_salud=0.5)
        self.assertIn("C-09 aprobado", salida.call_args.args[0])

    async def test_script_c09_no_aprueba_si_stock_ya_termino(self):
        def cliente_asgi(**kwargs):
            return AsyncClient(transport=ASGITransport(app=self.app), **kwargs)

        with (
            patch("c09_concurrencia.httpx.AsyncClient", side_effect=cliente_asgi),
            patch("app.modules.laboratorio.cliente.consultar_stock", return_value=15),
            patch("builtins.print"),
        ):
            with self.assertRaisesRegex(AssertionError, "consultas seguían pendientes"):
                await comprobar("http://prueba", limite_salud=0.5)
