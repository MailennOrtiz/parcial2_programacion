"""Pruebas HTTP sobre SQLite asincrónico en memoria; nunca usan el .env real."""

from fastapi import HTTPException

from app.main import app as app_real
from app.modules.duenios.schemas import DuenioCreate
from app.modules.duenios.service import crear_duenio
from soporte_api import ApiTestsBase


class CrudTests(ApiTestsBase):
    def test_rutas_registradas_en_aplicacion_real(self):
        rutas = app_real.openapi()["paths"]
        for ruta in ("/duenios/", "/duenios/{id}", "/duenios/{id}/ficha",
                     "/duenios/{id}/mascotas", "/mascotas/", "/mascotas/{id}", "/practicas/"):
            self.assertIn(ruta, rutas)

    def test_alta_duenio_sin_id_y_con_ficha_null(self):
        respuesta = self.client.post("/duenios/", json={"nombre": " Eva ", "email": "eva@example.com"})
        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(respuesta.json(), {"id": 3, "nombre": "Eva", "email": "eva@example.com", "ficha": None})
        # No hay consulta de existencia antes de intentar la escritura.
        self.assertTrue(self.sentencias[0].startswith("INSERT INTO duenio"))

    def test_detalle_duenio_con_ficha_en_una_consulta(self):
        respuesta = self.client.get("/duenios/1")
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json()["ficha"]["duenio_id"], 1)
        consultas = [sql for sql in self.sentencias if sql.startswith("SELECT")]
        self.assertEqual(len(consultas), 1)
        self.assertIn("JOIN ficha_duenio", consultas[0])

    def test_patch_solo_campos_enviados(self):
        respuesta = self.client.patch("/duenios/1", json={"nombre": "Ana actualizada"})
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json()["nombre"], "Ana actualizada")
        self.assertEqual(respuesta.json()["email"], "ana@example.com")
        self.assertIsNotNone(respuesta.json()["ficha"])
        vacio = self.client.patch("/duenios/1", json={})
        self.assertEqual(vacio.status_code, 200)
        self.assertEqual(vacio.json(), respuesta.json())

    def test_patch_email_duplicado_y_rollback(self):
        respuesta = self.client.patch("/duenios/1", json={"email": "luis@example.com"})
        self.assertEqual(respuesta.status_code, 409)
        self.assertEqual(self.client.get("/duenios/1").json()["email"], "ana@example.com")

    def test_email_repetido_y_session_reutilizable_tras_rollback(self):
        async def ejecutar():
            async with self.app.state.fabrica_de_sesiones() as session:
                with self.assertRaises(HTTPException) as contexto:
                    await crear_duenio(session, DuenioCreate(nombre="Duplicado", email="ana@example.com"))
                self.assertEqual(contexto.exception.status_code, 409)
                nuevo = await crear_duenio(session, DuenioCreate(nombre="Nuevo", email="nuevo@example.com"))
                return nuevo.email

        self.assertEqual(self.client.portal.call(ejecutar), "nuevo@example.com")

    def test_email_duplicado_responde_mensaje_propio(self):
        respuesta = self.client.post("/duenios/", json={"nombre": "Otra Ana", "email": "ana@example.com"})
        self.assertEqual(respuesta.status_code, 409)
        self.assertEqual(respuesta.json(), {"detail": "Ya existe un dueño con ese email."})
        self.assertNotIn("SELECT", self.sentencias[0])

    def test_ficha_nueva_segunda_ficha_y_404(self):
        datos = {"telefono": "123456", "direccion": "Calle 456"}
        respuesta = self.client.post("/duenios/2/ficha", json=datos)
        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(respuesta.json()["duenio_id"], 2)
        self.assertEqual(self.client.get("/duenios/2").json()["ficha"]["telefono"], "123456")
        self.assertEqual(self.client.post("/duenios/2/ficha", json=datos).status_code, 409)
        self.assertEqual(self.client.post("/duenios/999/ficha", json=datos).status_code, 404)

    def test_borrado_duenio_con_mascotas_devuelve_409(self):
        respuesta = self.client.delete("/duenios/1")
        self.assertEqual(respuesta.status_code, 409)
        self.assertEqual(self.client.get("/duenios/1").status_code, 200)
        self.assertEqual(len(self.client.get("/duenios/1/mascotas").json()), 2)

    def test_borrado_sin_mascotas_devuelve_204_sin_cuerpo(self):
        duenio = self.client.post("/duenios/", json={"nombre": "Sin mascotas", "email": "solo@example.com"}).json()
        id = duenio["id"]
        self.assertEqual(self.client.post(f"/duenios/{id}/ficha", json={"telefono": "1", "direccion": "Calle"}).status_code, 201)
        respuesta = self.client.delete(f"/duenios/{id}")
        self.assertEqual(respuesta.status_code, 204)
        self.assertEqual(respuesta.content, b"")
        self.assertEqual(self.client.get(f"/duenios/{id}").status_code, 404)
        self.assertEqual(self.client.delete(f"/duenios/{id}").status_code, 404)

    def test_mascotas_de_duenio_y_duenio_inexistente(self):
        respuesta = self.client.get("/duenios/1/mascotas")
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual([m["nombre"] for m in respuesta.json()], ["Toby", "Mora"])
        self.assertEqual(len([sql for sql in self.sentencias if sql.startswith("SELECT")]), 2)
        self.assertEqual(self.client.get("/duenios/999/mascotas").status_code, 404)
        nuevo = self.client.post("/duenios/", json={"nombre": "Solo", "email": "solo@example.com"}).json()
        self.assertEqual(self.client.get(f"/duenios/{nuevo['id']}/mascotas").json(), [])

    def test_alta_mascota_y_duenio_inexistente(self):
        datos = {"nombre": "Pepe", "especie": "loro", "duenio_id": 2}
        respuesta = self.client.post("/mascotas/", json=datos)
        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(respuesta.json()["duenio_id"], 2)
        self.assertTrue(self.sentencias[0].startswith("INSERT INTO mascota"))
        datos["duenio_id"] = 999
        self.assertEqual(self.client.post("/mascotas/", json=datos).status_code, 409)
        self.assertEqual(self.client.get("/mascotas/").json()["total"], 4)

    def test_detalle_mascota_con_duenio_precargado(self):
        respuesta = self.client.get("/mascotas/1")
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json()["duenio"]["email"], "ana@example.com")
        consultas = [sql for sql in self.sentencias if sql.startswith("SELECT")]
        self.assertEqual(len(consultas), 1)
        self.assertIn("JOIN duenio", consultas[0])

    def test_paginacion_predeterminada_y_ultima_pagina(self):
        respuesta = self.client.get("/mascotas/")
        self.assertEqual(respuesta.status_code, 200)
        datos = respuesta.json()
        self.assertEqual((datos["total"], datos["page"], datos["size"], datos["pages"]), (3, 1, 20, 1))
        ultima = self.client.get("/mascotas/?page=2&size=2").json()
        self.assertEqual(ultima["pages"], 2)
        self.assertEqual([m["id"] for m in ultima["items"]], [3])
        self.assertEqual(self.client.get("/mascotas/?page=3&size=2").status_code, 422)

    def test_pagina_uno_sin_resultados(self):
        # Solo en la base de prueba en memoria. Elimina las referencias primero.
        async def vaciar():
            from sqlalchemy import delete
            from app.core.modelos import Mascota, Turno, TurnoPractica

            async with self.app.state.fabrica_de_sesiones() as session:
                for modelo in (TurnoPractica, Turno, Mascota):
                    await session.exec(delete(modelo))
                await session.commit()

        self.client.portal.call(vaciar)
        respuesta = self.client.get("/mascotas/")
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json(), {"items": [], "total": 0, "page": 1, "size": 20, "pages": 0})
        self.assertEqual(self.client.get("/mascotas/?page=2").status_code, 422)

    def test_catalogo_alta_decimal_y_nombre_duplicado(self):
        catalogo = self.client.get("/practicas/")
        self.assertEqual(catalogo.status_code, 200)
        self.assertEqual(len(catalogo.json()), 4)
        self.assertEqual(catalogo.json()[0]["precio"], "15000.00")
        datos = {"nombre": "Ecografía", "precio": "123.45"}
        respuesta = self.client.post("/practicas/", json=datos)
        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(respuesta.json()["precio"], "123.45")
        self.assertEqual(self.client.post("/practicas/", json=datos).status_code, 409)

    def test_recursos_inexistentes(self):
        for metodo, ruta, cuerpo in (
            ("get", "/duenios/999", None), ("patch", "/duenios/999", {"nombre": "Otro"}),
            ("delete", "/duenios/999", None), ("get", "/mascotas/999", None),
        ):
            with self.subTest(metodo=metodo, ruta=ruta):
                argumentos = {} if cuerpo is None else {"json": cuerpo}
                self.assertEqual(getattr(self.client, metodo)(ruta, **argumentos).status_code, 404)

    def test_parametros_invalidos_sin_consultas(self):
        for ruta in ("/duenios/abc", "/duenios/0", "/mascotas/abc", "/mascotas/-1",
                     "/mascotas/?page=0", "/mascotas/?size=0", "/mascotas/?size=101",
                     "/mascotas/?page=abc"):
            with self.subTest(ruta=ruta):
                self.sentencias.clear()
                self.assertEqual(self.client.get(ruta).status_code, 422)
                self.assertEqual(self.sentencias, [])

    def test_contratos_rechazan_id_extras_null_y_datos_invalidos(self):
        casos = [
            ("post", "/duenios/", {"id": 8, "nombre": "Ana", "email": "x@example.com"}),
            ("post", "/duenios/", {"nombre": "   ", "email": "x@example.com"}),
            ("post", "/duenios/", {"nombre": "Ana", "email": "invalido"}),
            ("patch", "/duenios/1", {"nombre": None}),
            ("patch", "/duenios/1", {"email": None}),
            ("post", "/duenios/2/ficha", {"telefono": "", "direccion": "Calle"}),
            ("post", "/mascotas/", {"nombre": "Pepe", "especie": "loro", "duenio_id": 0}),
            ("post", "/practicas/", {"nombre": "Nueva", "precio": "0.00"}),
            ("post", "/practicas/", {"nombre": "Nueva", "precio": "-1.00"}),
            ("post", "/practicas/", {"nombre": "Nueva", "precio": "1.001"}),
            ("post", "/practicas/", {"nombre": "Nueva", "precio": "100000000.00"}),
        ]
        for metodo, ruta, datos in casos:
            with self.subTest(metodo=metodo, ruta=ruta, datos=datos):
                self.sentencias.clear()
                respuesta = getattr(self.client, metodo)(ruta, json=datos)
                self.assertEqual(respuesta.status_code, 422, respuesta.text)
                self.assertEqual(self.sentencias, [])
