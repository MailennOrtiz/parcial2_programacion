"""Pruebas HTTP con SQLite aislado; no sustituyen la prueba en PostgreSQL."""
import unittest

from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.main import app


class CrudTest(unittest.IsolatedAsyncioTestCase):
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

    async def asyncTearDown(self):
        await self.cliente.aclose()
        app.dependency_overrides.clear()
        await self.motor.dispose()

    async def alta(self, ruta, cuerpo):
        respuesta = await self.cliente.post(ruta, json=cuerpo)
        self.assertEqual(respuesta.status_code, 201, respuesta.text)
        return respuesta.json()

    async def test_editoriales_validacion_conflictos_y_patch(self):
        editorial = await self.alta("/editoriales/", {"nombre": "Sur", "pais": "Argentina"})
        duplicada = await self.cliente.post("/editoriales/", json={"nombre": "Sur"})
        self.assertEqual(duplicada.status_code, 409)
        self.assertNotIn("UNIQUE", duplicada.text)
        actualizada = await self.cliente.patch(f"/editoriales/{editorial['id']}", json={"nombre": "Norte"})
        self.assertEqual(actualizada.status_code, 200, actualizada.text)
        self.assertEqual(actualizada.json()["pais"], "Argentina")
        self.assertEqual((await self.cliente.patch("/editoriales/1", json={"nombre": None})).status_code, 422)
        self.assertEqual((await self.cliente.get("/editoriales/abc")).status_code, 422)
        self.assertEqual((await self.cliente.get("/editoriales/999")).status_code, 404)
        self.assertEqual((await self.cliente.get("/editoriales/?limit=101")).status_code, 422)
        self.assertEqual((await self.cliente.get("/editoriales/?offset=-1")).status_code, 422)

    async def test_libros_autores_filtrado_y_fk(self):
        editorial = await self.alta("/editoriales/", {"nombre": "Sur"})
        genero = await self.alta("/generos/", {"nombre": "Novela"})
        autor = await self.alta("/autores/", {"nombre": "Cortázar"})
        cuerpo = {"isbn": "123", "titulo": "Rayuela", "precio": "25000.00", "stock": 3,
                  "editorial_id": editorial["id"], "genero_id": genero["id"],
                  "autores": [{"autor_id": autor["id"], "rol": "autor", "orden": 1}]}
        libro = await self.alta("/libros/", cuerpo)
        self.assertEqual(libro["autores"][0]["autor"]["nombre"], "Cortázar")
        self.assertEqual(len((await self.cliente.get("/libros/", params={"titulo": "YUE"})).json()), 1)
        self.assertEqual((await self.cliente.get("/libros/", params={"titulo": "' OR '1'='1"})).json(), [])
        self.assertEqual((await self.cliente.get(f"/autores/{autor['id']}/libros")).status_code, 200)
        self.assertEqual((await self.cliente.get(f"/generos/{genero['id']}/libros")).status_code, 200)
        self.assertEqual((await self.cliente.get(f"/editoriales/{editorial['id']}/libros")).status_code, 200)
        cuerpo.update(isbn="456", editorial_id=999)
        self.assertEqual((await self.cliente.post("/libros/", json=cuerpo)).status_code, 409)

    async def test_clientes_perfil_y_venta(self):
        editorial = await self.alta("/editoriales/", {"nombre": "Sur"})
        libro = await self.alta("/libros/", {"isbn": "123", "titulo": "Rayuela", "precio": "25.00",
            "stock": 3, "editorial_id": editorial["id"], "autores": []})
        cliente = await self.alta("/clientes/", {"nombre": "Ana", "email": "ana@example.com"})
        perfil = {"telefono": "123", "direccion": "Calle 1"}
        await self.alta(f"/clientes/{cliente['id']}/perfil", perfil)
        self.assertEqual((await self.cliente.post(f"/clientes/{cliente['id']}/perfil", json=perfil)).status_code, 409)
        self.assertEqual((await self.cliente.get(f"/clientes/{cliente['id']}")).json()["perfil"]["telefono"], "123")
        cuerpo = {"cliente_id": cliente["id"], "renglones": [{"libro_id": libro["id"], "cantidad": 2}]}
        venta = await self.alta("/ventas/", cuerpo)
        self.assertEqual(venta["total"], "50.00")
        self.assertEqual(venta["renglones"][0]["titulo"], "Rayuela")
        await self.cliente.patch(f"/libros/{libro['id']}", json={"precio": "30.00"})
        detalle = (await self.cliente.get(f"/ventas/{venta['id']}")).json()
        self.assertEqual(detalle["renglones"][0]["precio_unitario"], "25.00")
        self.assertEqual((await self.cliente.get(f"/clientes/{cliente['id']}/ventas")).status_code, 200)
        self.assertEqual((await self.cliente.patch(f"/ventas/{venta['id']}", json={})).status_code, 405)
        cuerpo["renglones"].append(cuerpo["renglones"][0])
        self.assertEqual((await self.cliente.post("/ventas/", json=cuerpo)).status_code, 422)

    async def test_contratos_y_ventas_invalidas(self):
        editorial = await self.alta("/editoriales/", {"nombre": "Sur"})
        autor = await self.alta("/autores/", {"nombre": "Una autora", "nacionalidad": "Argentina"})
        actualizado = await self.cliente.patch(f"/autores/{autor['id']}", json={"nombre": "Otra autora"})
        self.assertEqual(actualizado.json()["nacionalidad"], "Argentina")
        self.assertEqual((await self.cliente.post("/autores/", json={"id": 1, "nombre": "X"})).status_code, 422)
        cuerpo = {"isbn": "123", "titulo": "Libro", "precio": "0.00", "stock": 1,
                  "editorial_id": editorial["id"], "autores": []}
        self.assertEqual((await self.cliente.post("/libros/", json=cuerpo)).status_code, 422)
        cuerpo["precio"] = "20.00"
        libro = await self.alta("/libros/", cuerpo)
        cliente = await self.alta("/clientes/", {"nombre": "Ana", "email": "ana@example.com"})
        self.assertEqual((await self.cliente.post("/clientes/", json={"nombre": "Otra", "email": "ana@example.com"})).status_code, 409)
        self.assertEqual((await self.cliente.patch(f"/clientes/{cliente['id']}", json={"email": None})).status_code, 422)
        self.assertEqual((await self.cliente.post("/ventas/", json={"cliente_id": cliente["id"], "renglones": []})).status_code, 422)
        self.assertEqual((await self.cliente.post("/ventas/", json={"cliente_id": cliente["id"],
            "renglones": [{"libro_id": 999, "cantidad": 1}]})).status_code, 409)
        self.assertEqual((await self.cliente.post("/ventas/", json={"cliente_id": 999,
            "renglones": [{"libro_id": libro["id"], "cantidad": 1}]})).status_code, 409)
        self.assertEqual((await self.cliente.get("/ventas/")).json(), [])
