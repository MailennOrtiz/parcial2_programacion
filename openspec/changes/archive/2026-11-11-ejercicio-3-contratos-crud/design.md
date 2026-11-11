# Design

## Context

La aplicación ya tiene el ciclo de vida, las sesiones asincrónicas y los modelos del dominio. El trabajo previo de veterinaria separa modelos, contratos, servicios y routers por módulo; se conserva esa estructura.

## Goals / Non-Goals

**Goals:**
- Cumplir los endpoints de referencia y los contratos del ejercicio 3.
- Mantener consultas parametrizadas, paginación y errores HTTP seguros.
- Evitar que la serialización dispare carga perezosa.

**Non-Goals:**
- No incorporar autenticación, repositorios, migraciones, Docker ni despliegue.
- No implementar endpoints de modificación de ventas, que registran hechos inmutables.

## Decisions

- **Contratos separados:** los DTO de creación no contienen id; los de actualización conservan únicamente los campos enviados mediante `exclude_unset`.
- **Integridad en la base:** capturar `IntegrityError`, ejecutar rollback y responder 409 con mensaje propio, sin verificación previa de unicidad.
- **Paginación:** `limit` entre 1 y 100, por defecto 20, y `offset` desde 0; ordenar por id para resultados estables.
- **Búsqueda:** expresión parametrizada de SQLAlchemy para coincidencias de título sin distinción de mayúsculas.
- **Relaciones:** precargar en la consulta las relaciones usadas por las respuestas; evitar ciclos con contratos resumidos.

## Risks / Trade-offs

- Las altas de libros y ventas y sus respuestas requieren capacidades también descritas en los ejercicios 4 y 5; deben mantenerse coherentes sin dar por comprobados esos ejercicios anticipadamente.
- Las pruebas con SQLite no sustituyen las comprobaciones reales de PostgreSQL para restricciones y tipos específicos.

## Migration Plan

No se cambian las tablas. `create_all` no modifica esquemas existentes; cualquier cambio posterior de modelos requerirá una base de desarrollo preparada por separado.

## Open Questions

- Ninguna que impida comenzar; los detalles no especificados deben seguir la consigna y el proyecto de referencia.
