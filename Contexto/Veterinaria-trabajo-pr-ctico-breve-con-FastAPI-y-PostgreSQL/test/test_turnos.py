"""Reserva y detalle de turnos sobre SQLite en memoria, sin tocar PostgreSQL."""

from decimal import Decimal
from unittest.mock import patch

from fastapi import HTTPException
from sqlalchemy import func
from sqlmodel import select

from app.core.modelos import Practica, Turno, TurnoPractica
from app.main import app as app_real
from app.modules.turnos.schemas import TurnoCreate
from app.modules.turnos.service import crear_turno, detalle_turno
from soporte_api import ApiTestsBase


class TurnosTests(ApiTestsBase):
    def cuerpo(self, ids=(1, 3), **cambios):
        datos = {
            "mascota_id": 1,
            "fecha": "2026-11-12T10:30:00-03:00",
            "motivo": "Control anual",
            "practicas": [{"practica_id": id} for id in ids],
        }
        datos.update(cambios)
        return datos

    def cantidades(self):
        async def consultar():
            async with self.app.state.fabrica_de_sesiones() as session:
                return tuple(
                    [(await session.exec(select(func.count()).select_from(modelo))).one()
                     for modelo in (Turno, TurnoPractica)]
                )

        return self.client.portal.call(consultar)

    def test_rutas_registradas(self):
        rutas = app_real.openapi()["paths"]
        self.assertIn("post", rutas["/turnos/"])
        self.assertIn("get", rutas["/turnos/{id}"])
        self.assertIn("delete", rutas["/turnos/{id}"])

    def test_alta_dos_practicas_respuesta_y_total(self):
        respuesta = self.client.post("/turnos/", json=self.cuerpo())
        self.assertEqual(respuesta.status_code, 201, respuesta.text)
        turno = respuesta.json()
        self.assertEqual(turno["id"], 2)
        self.assertEqual(turno["motivo"], "Control anual")
        self.assertEqual(turno["total"], "27000.00")
        self.assertEqual(turno["mascota"], {"id": 1, "nombre": "Toby", "especie": "perro"})
        self.assertEqual(turno["practicas"], [
            {"practica_id": 1, "nombre": "Consulta", "precio_unitario": "15000.00"},
            {"practica_id": 3, "nombre": "Vacuna antirrábica", "precio_unitario": "12000.00"},
        ])
        self.assertEqual(self.cantidades(), (2, 4))
        # Se normaliza a UTC antes de guardar. SQLite no conserva el tzinfo;
        # PostgreSQL sí devuelve la zona en TIMESTAMP WITH TIME ZONE.
        self.assertTrue(turno["fecha"].startswith("2026-11-12T13:30:00"))

    def test_alta_una_practica_y_orden_de_respuesta(self):
        una = self.client.post("/turnos/", json=self.cuerpo((2,)))
        self.assertEqual(una.status_code, 201)
        self.assertEqual(una.json()["total"], "8000.00")
        desordenadas = self.client.post("/turnos/", json=self.cuerpo((3, 1)))
        self.assertEqual(desordenadas.status_code, 201)
        self.assertEqual([p["practica_id"] for p in desordenadas.json()["practicas"]], [1, 3])

    def test_detalle_turno_inicial(self):
        respuesta = self.client.get("/turnos/1")
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json()["total"], "27000.00")
        self.assertEqual(len(respuesta.json()["practicas"]), 2)

    def test_detalle_una_y_tres_practicas_emiten_dos_selects(self):
        for ids in ((1,), (1, 2, 3)):
            with self.subTest(ids=ids):
                alta = self.client.post("/turnos/", json=self.cuerpo(ids))
                self.assertEqual(alta.status_code, 201)
                self.sentencias.clear()
                respuesta = self.client.get(f"/turnos/{alta.json()['id']}")
                self.assertEqual(respuesta.status_code, 200)
                self.assertEqual(len(respuesta.json()["practicas"]), len(ids))
                consultas = [sql for sql in self.sentencias if sql.startswith("SELECT")]
                self.assertEqual(len(consultas), 2)
                self.assertIn("JOIN mascota", consultas[0])
                self.assertIn("JOIN practica", consultas[1])

    def test_solo_una_consulta_de_catalogo_en_alta(self):
        for ids in ((1,), (1, 2, 3)):
            self.sentencias.clear()
            respuesta = self.client.post("/turnos/", json=self.cuerpo(ids))
            self.assertEqual(respuesta.status_code, 201)
            consultas = [sql for sql in self.sentencias if sql.startswith("SELECT")]
            self.assertEqual(len(consultas), 3)  # Catálogo + dos de lectura de respuesta.
            self.assertIn("FROM practica", consultas[0])
            self.assertNotIn("SELECT mascota", consultas[0])

    def test_practica_inexistente_no_guarda_nada(self):
        antes = self.cantidades()
        respuesta = self.client.post("/turnos/", json=self.cuerpo((1, 999999)))
        self.assertEqual(respuesta.status_code, 409)
        self.assertIn("No se guardó", respuesta.json()["detail"])
        self.assertEqual(self.cantidades(), antes)

    def test_todas_las_practicas_inexistentes_no_guardan_turno(self):
        antes = self.cantidades()
        respuesta = self.client.post("/turnos/", json=self.cuerpo((999998, 999999)))
        self.assertEqual(respuesta.status_code, 409)
        self.assertEqual(self.cantidades(), antes)

    def test_mascota_inexistente_no_guarda_nada(self):
        antes = self.cantidades()
        respuesta = self.client.post("/turnos/", json=self.cuerpo(mascota_id=999999))
        self.assertEqual(respuesta.status_code, 409)
        self.assertEqual(self.cantidades(), antes)

    def test_practica_repetida_la_rechaza_pk_compuesta(self):
        antes = self.cantidades()
        self.sentencias.clear()
        respuesta = self.client.post("/turnos/", json=self.cuerpo((1, 3, 1)))
        self.assertEqual(respuesta.status_code, 409)
        self.assertTrue(any(sql.startswith("INSERT INTO turno_practica") for sql in self.sentencias))
        self.assertEqual(self.cantidades(), antes)

    def test_session_reutilizable_despues_de_rollback(self):
        async def ejecutar():
            async with self.app.state.fabrica_de_sesiones() as session:
                for ids in ((1, 999999), (1, 1)):
                    with self.assertRaises(HTTPException) as contexto:
                        await crear_turno(session, TurnoCreate.model_validate(self.cuerpo(ids)))
                    self.assertEqual(contexto.exception.status_code, 409)
                valido = await crear_turno(session, TurnoCreate.model_validate(self.cuerpo()))
                return valido.total

        self.assertEqual(self.client.portal.call(ejecutar), Decimal("27000.00"))
        self.assertEqual(self.cantidades(), (2, 4))

    def test_un_solo_commit_para_turno_y_partes(self):
        async def ejecutar():
            async with self.app.state.fabrica_de_sesiones() as session:
                with patch.object(session, "commit", wraps=session.commit) as commit:
                    await crear_turno(session, TurnoCreate.model_validate(self.cuerpo()))
                    commit.assert_awaited_once()

        self.client.portal.call(ejecutar)

    def test_precio_del_turno_no_cambia_con_catalogo(self):
        async def cambiar_catalogo():
            async with self.app.state.fabrica_de_sesiones() as session:
                practica = await session.get(Practica, 1)
                practica.precio = Decimal("20000.00")
                await session.commit()

        self.client.portal.call(cambiar_catalogo)
        inicial = self.client.get("/turnos/1").json()
        self.assertEqual(inicial["total"], "27000.00")
        self.assertEqual(inicial["practicas"][0]["precio_unitario"], "15000.00")
        nuevo = self.client.post("/turnos/", json=self.cuerpo()).json()
        self.assertEqual(nuevo["total"], "32000.00")
        self.assertEqual(nuevo["practicas"][0]["precio_unitario"], "20000.00")

    def test_borrado_cascada_sin_delete_de_partes_por_orm(self):
        self.sentencias.clear()
        respuesta = self.client.delete("/turnos/1")
        self.assertEqual(respuesta.status_code, 204)
        self.assertEqual(respuesta.content, b"")
        deletes = [sql for sql in self.sentencias if sql.startswith("DELETE")]
        self.assertEqual(len(deletes), 1)
        self.assertTrue(deletes[0].startswith("DELETE FROM turno "))
        self.assertEqual(self.cantidades(), (0, 0))
        self.assertEqual(len(self.client.get("/practicas/").json()), 4)
        self.assertEqual(self.client.get("/mascotas/1").status_code, 200)

    def test_borrado_con_coleccion_ya_precargada(self):
        async def borrar_precargado():
            from app.modules.turnos.service import borrar_turno, obtener_turno

            async with self.app.state.fabrica_de_sesiones() as session:
                turno = await obtener_turno(session, 1)
                self.assertEqual(len(turno.practicas), 2)
                self.sentencias.clear()
                await borrar_turno(session, 1)

        self.client.portal.call(borrar_precargado)
        deletes = [sql for sql in self.sentencias if sql.startswith("DELETE")]
        self.assertEqual(len(deletes), 1)
        self.assertTrue(deletes[0].startswith("DELETE FROM turno "))
        self.assertEqual(self.cantidades(), (0, 0))

    def test_lectura_dto_funciona_tras_cerrar_session(self):
        async def leer():
            async with self.app.state.fabrica_de_sesiones() as session:
                return await detalle_turno(session, 1)

        dto = self.client.portal.call(leer)
        self.assertEqual(dto.mascota.nombre, "Toby")
        self.assertEqual(dto.practicas[0].nombre, "Consulta")

    def test_404_al_leer_y_borrar_inexistente(self):
        self.assertEqual(self.client.get("/turnos/999999").status_code, 404)
        self.assertEqual(self.client.delete("/turnos/999999").status_code, 404)

    def test_parametros_invalidos_no_ejecutan_handler(self):
        for metodo in ("get", "delete"):
            for id in ("abc", "0", "-1"):
                self.sentencias.clear()
                self.assertEqual(getattr(self.client, metodo)(f"/turnos/{id}").status_code, 422)
                self.assertEqual(self.sentencias, [])

    def test_lista_vacia_y_contratos_invalidos_sin_sql(self):
        cuerpos = [
            self.cuerpo(()),
            self.cuerpo(mascota_id=0),
            self.cuerpo(fecha="2026-11-12T10:30:00"),
            self.cuerpo(fecha="no es fecha"),
            self.cuerpo(motivo="   "),
            self.cuerpo(total="1.00"),
            self.cuerpo(id=100),
            self.cuerpo(practicas=[{"practica_id": 0}]),
            self.cuerpo(practicas=[{"practica_id": 1, "precio_unitario": "1.00"}]),
            self.cuerpo(practicas=[{"practica_id": 1, "precio": "1.00"}]),
            self.cuerpo(practicas=[1, 3]),
        ]
        sin_practicas = self.cuerpo()
        del sin_practicas["practicas"]
        cuerpos.append(sin_practicas)
        for cuerpo in cuerpos:
            with self.subTest(cuerpo=cuerpo):
                self.sentencias.clear()
                respuesta = self.client.post("/turnos/", json=cuerpo)
                self.assertEqual(respuesta.status_code, 422, respuesta.text)
                self.assertEqual(self.sentencias, [])
