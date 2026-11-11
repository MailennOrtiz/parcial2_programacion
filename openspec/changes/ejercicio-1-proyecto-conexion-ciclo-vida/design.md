# Design

## Context

Ver `proposal.md` - Why. El proyecto parte de cero: no hay código ni esquema. La base es PostgreSQL 16 (local o del VPS) y se accede con asyncpg. Las tablas aún no existen porque los modelos de dominio se implementan en ejercicios posteriores; `create_all` debe importar todos los modelos para que, cuando existan, se creen automáticamente.

## Goals / Non-Goals

**Goals:**
- Establecer la estructura por módulos y el ciclo de vida de FastAPI.
- Centralizar la configuración de la base en `app/core/config.py` y `app/core/database.py`.
- Proveer dependencia `get_session` reutilizable.
- Exponer endpoints de salud compatibles con el HEALTHCHECK del contenedor.

**Non-Goals:**
- No se implementan modelos de dominio ni CRUD (ejercicios posteriores).
- No se configura Docker ni despliegue (ejercicio 7/8).
- No se agregan migraciones (fuera de alcance de la consigna).

## Decisions

- **Motor y fábrica en `lifespan`**: se crean en el startup y se guardan en `app.state`; se cierran en shutdown. Alternativa (crearlos a nivel de módulo) se descarta porque dificulta el cierre limpio y los tests.
- **Sesión por petición con `expire_on_commit=False`**: permite leer atributos tras el commit sin recargar; alternativa con `expire_on_commit=True` fuerza recargas y puede disparar lazy loading prohibido.
- **`create_all` en startup**: crea tablas faltantes sin alterar existentes; alternativa con migraciones (Alembic) queda fuera de alcance.
- **Configuración por `DATABASE_URL` con `python-dotenv`**: sin valor por defecto, para que falte explícitamente y no se filtren secretos.
- **Healthcheck con `127.0.0.1`**: Alpine no tiene curl; se usa `wget` a `127.0.0.1` (no `localhost`, que resuelve a IPv6 y falla contra uvicorn en IPv4).

## Risks / Trade-offs

- [Riesgo] `create_all` no altera tablas existentes: un cambio de modelo no se refleja en una base ya creada. → Mitigación: documentar que en desarrollo se recrea la base; migraciones fuera de alcance.
- [Riesgo] Falta de `DATABASE_URL` en contenedor: el arranque falla (comportamiento deseado para D-05).
- [Riesgo] `wget` a `localhost` falla por IPv6 en Alpine. → Mitigación: HEALTHCHECK usa `127.0.0.1`.

## Migration Plan

No aplica (proyecto nuevo). El esquema se crea automáticamente al arrancar sobre una base vacía.

## Open Questions

- Ninguna que afecte specs o tareas. Los nombres de módulos y rutas siguen la consigna.