# Proposal

## Why

El parcial requiere una API asincrónica con FastAPI que se conecte a PostgreSQL de forma no bloqueante. El primer punto establece la base del proyecto: estructura por módulos, motor y fábrica de sesiones creados en el ciclo de vida de la aplicación, lectura de la URL de la base desde `.env`, creación del esquema al arrancar y endpoints de salud que distinguen "vivo" de "listo". Sin esta fundación, el resto de los ejercicios no puede implementarse ni probarse.

## What Changes

- Se crea la estructura obligatoria del proyecto: `app/main.py`, `app/core/config.py`, `app/core/database.py`, módulos funcionales (`health`, `editoriales`, `generos`, `autores`, `libros`, `clientes`, `ventas`) con sus archivos `models.py`, `schemas.py`, `service.py`, `router.py`, y la carpeta `test/`.
- Se implementa el `lifespan` de FastAPI: crea el motor asincrónico y la fábrica de sesiones, los guarda en `app.state` y los cierra al apagar.
- Se implementa `get_session` como dependencia (`Depends`), con una sesión por petición y `expire_on_commit=False`.
- Se lee `DATABASE_URL` desde el entorno mediante `python-dotenv`, con `env.example` sin secretos.
- Al arrancar se ejecuta `SQLModel.metadata.create_all` con todos los modelos ya importados.
- Se exponen `GET /health/live` (sin tocar la base) y `GET /health/ready` (ejecuta `SELECT 1`, responde 503 si falla).
- Se agregan `requirements.txt`, `.dockerignore`-compatible y documentación base (`README.md`, `DEPLOY.md` se completan en ejercicios posteriores).

## Capabilities

### New Capabilities
- `application-lifecycle`: ciclo de vida de la aplicación (lifespan, motor asincrónico, fábrica de sesiones, `app.state`, cierre al apagar), dependencia de sesión por petición con `expire_on_commit=False`, lectura de `DATABASE_URL` desde el entorno y creación del esquema con `create_all` al arrancar.
- `health-checks`: endpoints `GET /health/live` y `GET /health/ready`, este último verificando la base con `SELECT 1` y respondiendo 503 ante fallo.

### Modified Capabilities
<!-- Ninguna: es el primer ejercicio, no hay specs previas. -->

## Impact

- Código afectado: nuevo árbol `app/` y `test/`.
- APIs: nuevos endpoints `/health/live` y `/health/ready`.
- Dependencias: FastAPI, SQLModel, SQLAlchemy asincrónico, asyncpg, python-dotenv, uvicorn.
- Sistemas: PostgreSQL 16 (base provista por la cátedra en despliegue).