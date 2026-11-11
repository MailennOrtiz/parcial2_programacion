"""Verifica metadatos y SQL de PostgreSQL sin conectarse ni modificar la base."""

from datetime import datetime, timezone
from decimal import Decimal
import unittest

from sqlalchemy import CheckConstraint, UniqueConstraint, inspect
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import configure_mappers
from sqlalchemy.schema import CreateTable
from sqlmodel import SQLModel

from app.core.modelos import Duenio, FichaDuenio, Mascota, Practica, Turno, TurnoPractica


class ModelosTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        configure_mappers()

    def test_tablas_y_columnas_obligatorias(self):
        esperadas = {
            "duenio": {"id", "nombre", "email"},
            "ficha_duenio": {"id", "duenio_id", "telefono", "direccion"},
            "mascota": {"id", "nombre", "especie", "duenio_id"},
            "practica": {"id", "nombre", "precio"},
            "turno": {"id", "mascota_id", "fecha", "motivo", "total"},
            "turno_practica": {"turno_id", "practica_id", "precio_unitario"},
        }
        self.assertEqual(set(SQLModel.metadata.tables), set(esperadas))
        for nombre, columnas in esperadas.items():
            with self.subTest(tabla=nombre):
                tabla = SQLModel.metadata.tables[nombre]
                self.assertEqual(set(tabla.columns.keys()), columnas)
                self.assertTrue(all(not columna.nullable for columna in tabla.columns))

    def test_unicidad(self):
        for modelo, columna in ((Duenio, "email"), (FichaDuenio, "duenio_id"), (Practica, "nombre")):
            with self.subTest(modelo=modelo.__name__):
                restricciones = [
                    set(r.columns.keys()) for r in modelo.__table__.constraints
                    if isinstance(r, UniqueConstraint)
                ]
                self.assertIn({columna}, restricciones)

    def test_checks(self):
        for modelo, expresion in (
            (Practica, "precio > 0"),
            (Turno, "total >= 0"),
            (TurnoPractica, "precio_unitario > 0"),
        ):
            with self.subTest(modelo=modelo.__name__):
                checks = {
                    str(r.sqltext) for r in modelo.__table__.constraints
                    if isinstance(r, CheckConstraint)
                }
                self.assertIn(expresion, checks)

    def test_claves_foraneas_y_borrado(self):
        for modelo, columna, destino, borrado in (
            (FichaDuenio, "duenio_id", "duenio.id", "CASCADE"),
            (Mascota, "duenio_id", "duenio.id", "RESTRICT"),
            (Turno, "mascota_id", "mascota.id", "RESTRICT"),
            (TurnoPractica, "turno_id", "turno.id", "CASCADE"),
            (TurnoPractica, "practica_id", "practica.id", "RESTRICT"),
        ):
            with self.subTest(modelo=modelo.__name__, columna=columna):
                fk, = modelo.__table__.c[columna].foreign_keys
                self.assertEqual(fk.target_fullname, destino)
                self.assertEqual(fk.ondelete, borrado)

    def test_indices_y_pk_compuesta(self):
        for modelo, columna in ((Mascota, "duenio_id"), (Turno, "mascota_id"), (TurnoPractica, "practica_id")):
            self.assertIn(
                [columna], [list(indice.columns.keys()) for indice in modelo.__table__.indexes]
            )
        tabla = TurnoPractica.__table__
        self.assertEqual(list(tabla.primary_key.columns.keys()), ["turno_id", "practica_id"])
        self.assertNotIn(["turno_id"], [list(i.columns.keys()) for i in tabla.indexes])

    def test_precision_y_zona_horaria(self):
        for modelo, columna, precision in (
            (Practica, "precio", 10), (Turno, "total", 12), (TurnoPractica, "precio_unitario", 10)
        ):
            tipo = modelo.__table__.c[columna].type
            self.assertEqual((tipo.precision, tipo.scale), (precision, 2))
            self.assertTrue(tipo.asdecimal)
        self.assertTrue(Turno.__table__.c.fecha.type.timezone)

    def test_relaciones_en_ambos_extremos(self):
        for modelo in (Duenio, FichaDuenio, Mascota, Practica, Turno, TurnoPractica):
            mapper = inspect(modelo)
            for relacion in mapper.relationships:
                with self.subTest(modelo=modelo.__name__, relacion=relacion.key):
                    inversa = relacion.mapper.relationships[relacion.back_populates]
                    self.assertIs(inversa.mapper.class_, modelo)
                    self.assertEqual(inversa.back_populates, relacion.key)
            for fk in modelo.__table__.foreign_keys:
                self.assertTrue(any(fk.parent in r.local_columns for r in mapper.relationships))
        self.assertFalse(inspect(Duenio).relationships.ficha.uselist)

    def test_borrado_delegado_en_base(self):
        for modelo, atributo in ((Turno, "practicas"), (Duenio, "mascotas"), (Duenio, "ficha")):
            relacion = inspect(modelo).relationships[atributo]
            self.assertEqual(relacion.passive_deletes, "all")
            self.assertNotIn("delete", relacion.cascade)
            self.assertNotIn("delete-orphan", relacion.cascade)

    def test_navegacion_en_memoria(self):
        duenio = Duenio(nombre="Ana", email="ana@example.com")
        ficha = FichaDuenio(telefono="123", direccion="Calle 1", duenio=duenio)
        mascota = Mascota(nombre="Toby", especie="perro", duenio=duenio)
        practica = Practica(nombre="Consulta", precio=Decimal("15000.00"))
        turno = Turno(
            mascota=mascota, fecha=datetime(2026, 11, 12, tzinfo=timezone.utc),
            motivo="Control", total=Decimal("15000.00"),
        )
        linea = TurnoPractica(turno=turno, practica=practica, precio_unitario=practica.precio)
        self.assertIs(duenio.ficha, ficha)
        self.assertIn(mascota, duenio.mascotas)
        self.assertIn(turno, mascota.turnos)
        self.assertIn(linea, turno.practicas)
        self.assertIn(linea, practica.turnos)
        self.assertIsInstance(linea.precio_unitario, Decimal)

    def test_ddl_postgresql(self):
        ddl = "\n".join(
            str(CreateTable(tabla).compile(dialect=postgresql.dialect()))
            for tabla in SQLModel.metadata.sorted_tables
        )
        for fragmento in (
            "TIMESTAMP WITH TIME ZONE", "NUMERIC(10, 2)", "NUMERIC(12, 2)",
            "PRIMARY KEY (turno_id, practica_id)", "ON DELETE CASCADE", "ON DELETE RESTRICT",
            "UNIQUE (email)", "UNIQUE (duenio_id)", "UNIQUE (nombre)",
        ):
            self.assertIn(fragmento, ddl)
