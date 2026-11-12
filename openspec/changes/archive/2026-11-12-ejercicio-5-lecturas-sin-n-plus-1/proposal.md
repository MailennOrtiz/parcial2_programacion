# Proposal: Ejercicio 5 - Lecturas sin N+1

## Why

El parcial exige que toda respuesta que incluya datos de una relación los obtenga con carga anticipada declarada en la misma consulta (`joinedload` para relaciones a uno y `selectinload` para colecciones), sin depender de carga perezosa y con un número fijo de consultas que no crezca con la cantidad de autores o renglones. Los ejercicios previos implementaron estas cargas de forma parcial; este change audita, endurece y verifica todos los caminos de lectura para que el caso C-07 (detalle de libro y de venta) sea determinista y medible.

## What Changes

- Auditar todos los caminos de lectura (libros, ventas, clientes, autores, editoriales, géneros) y garantizar `joinedload` (a uno) / `selectinload` (colecciones) más `raiseload("*")` donde corresponda.
- Convertir los retornos de ORM crudo en construcciones explícitas de DTO (`lectura(...)`) donde todavía se dependa de la serialización de FastAPI/SQLModel para evitar accesos perezosos.
- Añadir una prueba automatizada C-07 que cuente consultas SQL mediante listeners de SQLAlchemy y afirme un número fijo para `GET /libros/{id}` y `GET /ventas/{id}` con 1 vs. N autores/renglones.
- Añadir `test/05_lecturas_n_plus_1.http` con casos C-07 y guía para ejecutar con `SQL_ECHO`.
- Documentar en el spec delta el requisito de número fijo de consultas y la guardia `raiseload`.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `library-crud`: se refuerza el requisito "Lecturas relacionadas" para exigir número fijo de consultas, `joinedload` para relaciones a uno, `selectinload` para colecciones y `raiseload("*")` como guardia contra carga perezosa.

## Impact

- Módulos afectados: `app/modules/libros`, `app/modules/ventas`, `app/modules/clientes`, `app/modules/autores`, `app/modules/editoriales`, `app/modules/generos`, `app/core/crud.py`.
- Pruebas: `test/test_crud.py` (o nueva suite) y `test/05_lecturas_n_plus_1.http`.
- Sin cambios de endpoints, modelo de dominio ni migraciones.