# Design: Ejercicio 5 - Lecturas sin N+1

## Context

Ver `proposal.md` - Why. El código actual ya implementa cargas anticipadas en los servicios principales, pero con inconsistencias: `libros/listar` y `autores/libros` devuelven ORM crudo y `editoriales`/`generos` delegan en `libros_service.listar`; `clientes/obtener` devuelve ORM crudo con `joinedload` perfil; `autores/obtener` usa `crud.obtener` (sin relaciones, pero `AutorRead` no las incluye). El riesgo está en la serialización de FastAPI/SQLModel sobre ORM con relaciones no cargadas, que puede disparar carga perezosa o fallar con `raiseload`.

## Goals / Non-Goals

**Goals:**
- Garantizar carga anticipada declarada en la misma consulta para toda lectura con relaciones.
- Usar `joinedload` para relaciones a uno y `selectinload` para colecciones.
- Añadir `raiseload("*")` como guardia en toda consulta que alimente una respuesta con relaciones.
- Convertir retornos de ORM crudo a DTOs construidos en el servicio donde exista riesgo de acceso perezoso.
- Proveer una prueba C-07 que cuente consultas y afirme número fijo.

**Non-Goals:**
- No nuevos endpoints ni cambios al modelo de dominio.
- No migraciones ni cambios de Docker.
- No cambios a contratos (schemas) existentes.

## Decisions

1. **DTOs en lectura vs. ORM crudo.** Los servicios que devuelven entidades con relaciones (`libros/obtener`, `ventas/obtener`, `clientes/obtener`) ya construyen DTOs (`lectura(...)`). `libros/listar` y `autores/libros` deben seguir construyendo DTOs (`LibroResumenRead` / `LibroDeAutorRead`) en el servicio o en el router, para que la serialización no toque relaciones no cargadas. Alternativa (devolver ORM y confiar en `response_model`) se descarta porque FastAPI puede acceder a atributos no cargados.

2. **`raiseload("*")` como guardia global.** Se mantiene en `opciones()` de libros y ventas y en las consultas de autores/clientes. `crud.obtener`/`crud.listar` solo se usan para entidades sin relaciones en la respuesta (Editorial, Genero, Autor, y listados de esos módulos), por lo que no requieren carga anticipada; se documenta esta invariante.

3. **Conteo de consultas C-07.** Se usa un listener de eventos SQLAlchemy (`before_cursor_execute` o `after_cursor_execute`) sobre el engine de prueba para contar sentencias `SELECT`, aislando por caso. La prueba compara el conteo con 1 autor vs. N autores y con 1 vs. N renglones.

4. **`populate_existing=True`.** Se mantiene en consultas de detalle para evitar identidades stale del identity map durante pruebas.

## Risks / Trade-offs

- [SQLite vs. PostgreSQL] Las pruebas usan SQLite en memoria; el conteo de consultas puede diferir en dialecto pero la estructura de eager loading es equivalente. → La prueba C-07 se valida también manualmente con `SQL_ECHO` sobre PostgreSQL.
- [Serialización de SQLModel] SQLModel puede acceder a relaciones durante la validación. → Construcción explícita de DTOs en servicio elimina el riesgo.
- [N+1 oculto en `autores/libros`] `LibroResumenRead` incluye editorial/género; la consulta ya carga ambos. → Verificar que no se acceda a `libro.autorias`.

## Migration Plan

No aplica: sin migraciones ni cambios de esquema. Despliegue directo del código.

## Open Questions

Ninguna.