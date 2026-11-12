"""Prueba C-07: número fijo de consultas SQL en lecturas con relaciones."""
import unittest

from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.main import app


class NPlusOneTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.motor = create_async_engine("sqlite+aiosqlite:///:memory:")

        @event.listens_for(self.motor.sync_engine, "connect")
        def activar_fk(dbapi_connection, _):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        async with self.motor.begin() as conexion:
            await conexion.run_sync(SQLModel.metadata.create_all)
        fabrica = async_sessionmaker(self.motor, class_=AsyncSession, expire_on_commit=False)

        async def sesion_prueba():
            async with fabrica() as sesion:
                yield sesion

        app.dependency_overrides[get_session] = sesion_prueba
        self.cliente = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
        self.contador = {"n": 0}

        def contar(_conn, _cursor, statement, _parameters, _context, _executemany):
            if statement.lstrip().upper().startswith("SELECT"):
                self.contador["n"] += 1

        event.listen(self.motor.sync_engine, "before_cursor_execute", contar)

    async def asyncTearDown(self):
        await self.cliente.aclose()
        app.dependency_overrides.clear()
        await self.motor.dispose()

    async def alta(self, ruta, cuerpo):
        respuesta = await self.cliente.post(ruta, json=cuerpo)
        self.assertEqual(respuesta.status_code, 201, respuesta.text)
        return respuesta.json()

    def reset(self):
        self.contador["n"] = 0

    async def test_libro_detalle_consultas_fijas(self):
        editorial = await self.alta("/editoriales/", {"nombre": "Sur"})
        genero = await self.alta("/generos/", {"nombre": "Novela"})

        autor_uno = await self.alta("/autores/", {"nombre": "Autor Uno"})
        libro_uno = await self.alta("/libros/", {
            "isbn": "1", "titulo": "Libro Uno", "precio": "25.00", "stock": 3,
            "editorial_id": editorial["id"], "genero_id": genero["id"],
            "autores": [{"autor_id": autor_uno["id"], "rol": "autor", "orden": 1}],
        })
        self.reset()
        respuesta_uno = await self.cliente.get(f"/libros/{libro_uno['id']}")
        self.assertEqual(respuesta_uno.status_code, 200, respuesta_uno.text)
        consultas_uno = self.contador["n"]

        autores = [await self.alta("/autores/", {"nombre": f"Autor {i}"}) for i in range(5)]
        libro_n = await self.alta("/libros/", {
            "isbn": "2", "titulo": "Libro N", "precio": "25.00", "stock": 3,
            "editorial_id": editorial["id"], "genero_id": genero["id"],
            "autores": [{"autor_id": a["id"], "rol": "autor", "orden": i + 1}
                        for i, a in enumerate(autores)],
        })
        self.reset()
        respuesta_n = await self.cliente.get(f"/libros/{libro_n['id']}")
        self.assertEqual(respuesta_n.status_code, 200, respuesta_n.text)
        consultas_n = self.contador["n"]

        self.assertEqual(consultas_uno, consultas_n)
        self.assertGreater(consultas_uno, 0)

    async def test_venta_detalle_consultas_fijas(self):
        editorial = await self.alta("/editoriales/", {"nombre": "Sur"})
        libro = await self.alta("/libros/", {"isbn": "1", "titulo": "Rayuela",
            "precio": "25.00", "stock": 3, "editorial_id": editorial["id"],
            "autores": []})
        cliente = await self.alta("/clientes/", {"nombre": "Ana", "email": "ana@example.com"})

        venta_uno = await self.alta("/ventas/", {
            "cliente_id": cliente["id"],
            "renglones": [{"libro_id": libro["id"], "cantidad": 2}],
        })
        self.reset()
        respuesta_uno = await self.cliente.get(f"/ventas/{venta_uno['id']}")
        self.assertEqual(respuesta_uno.status_code, 200, respuesta_uno.text)
        consultas_uno = self.contador["n"]

        libros = [await self.alta("/libros/", {
            "isbn": f"isbn{i}", "titulo": f"Libro {i}", "precio": "10.00",
            "stock": 3, "editorial_id": editorial["id"], "autores": []})
            for i in range(5)]
        venta_n = await self.alta("/ventas/", {
            "cliente_id": cliente["id"],
            "renglones": [{"libro_id": l["id"], "cantidad": 1} for l in libros],
        })
        self.reset()
        respuesta_n = await self.cliente.get(f"/ventas/{venta_n['id']}")
        self.assertEqual(respuesta_n.status_code, 200, respuesta_n.text)
        consultas_n = self.contador["n"]

        self.assertEqual(consultas_uno, consultas_n)
        self.assertGreater(consultas_uno, 0)